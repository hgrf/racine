from datetime import date, datetime
from flask import jsonify, request
from marshmallow import fields

from . import api
from .samples import validate_sample_access
from .common import OrderedSchema
from .errors import bad_request
from ..main.forms import MarkAsNewsForm, NewActionForm

from ..common import db
from ..models import Action, News, Sample, record_activity, token_auth


class NewActionFormContent(OrderedSchema):
    csrf_token = fields.Str(metadata={"description": "CSRF (Cross Site Request Forgery) token"})
    timestamp = fields.Date(metadata={"description": "date of the action"})
    description = fields.Str(metadata={"description": "description of the action"})


class SwapActionOrderContent(OrderedSchema):
    actionid = fields.Int(metadata={"description": "Numeric ID of the first action"})
    swapid = fields.Int(
        metadata={"description": "Numeric ID of the second action for swapping order"}
    )


class MarkAsNewsContent(OrderedSchema):
    csrf_token = fields.Str(metadata={"description": "CSRF (Cross Site Request Forgery) token"})
    title = fields.Str(metadata={"description": "title of the news"})
    expires = fields.Date(metadata={"description": "expiration date of the news"})
    actionid = fields.Int(metadata={"description": "Numeric ID of the action to mark as news"})


@api.route("/action/<int:sampleid>", methods=["PUT"])
@token_auth.login_required
@validate_sample_access
def createaction(sample):
    """Create an action in the database.
    ---
    put:
      operationId: createAction
      description: Create an action in the database.
      tags: [actions]
      parameters:
      - in: path
        name: sampleid
        schema:
          type: integer
        required: true
        description: Numeric ID of the sample to add the action to.
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema: NewActionFormContent
      responses:
        201:
          description: Action created
        400:
          content:
            application/json:
              schema:
                type: object
                properties:
                  resubmit:
                    type: boolean
                    description: Form was not validated, but user should resubmit.
          description: Failed to create action
    """
    form = NewActionForm()
    if form.validate_on_submit():
        a = Action(
            datecreated=date.today(),
            timestamp=form.timestamp.data,
            owner=token_auth.current_user(),
            sample_id=sample.id,
            description=form.description.data,
        )
        db.session.add(a)
        record_activity("add:action", token_auth.current_user(), sample)
        db.session.commit()
        a.ordnum = a.id  # add ID as order number (maybe there is a more elegant way to do this?)
        db.session.commit()
    # if form was submitted but failed validation, show again to user
    # this is very important for the case where form is not validated because the
    # CSRF token passed its time limit (typically 3600s) -> users lose everything they
    # wrote otherwise (also happens when user enters invalid date)
    elif form.is_submitted():
        return jsonify(resubmit=True), 400

    return "", 201


@api.route("/action/<int:id>", methods=["DELETE"])
@token_auth.login_required
def deleteaction(id):
    """Delete an action from the database.
    ---
    delete:
      operationId: deleteAction
      description: Delete an action from the database.
      tags: [actions]
      parameters:
      - in: path
        name: id
        schema:
          type: integer
        required: true
        description: Numeric ID of the action to delete.
      responses:
        204:
          description: Action deleted
    """
    action = Action.query.get(id)
    if action is None or not action.has_write_access(token_auth.current_user()):
        return bad_request("You do not have permission to delete this action.")
    sampleid = action.sample_id
    db.session.delete(action)
    record_activity("delete:action", token_auth.current_user(), Sample.query.get(sampleid))
    db.session.commit()
    return "", 204


# TODO: sort out permissions for this (e.g. who has the right to change order?)
@api.route("/action/swaporder", methods=["POST"])
@token_auth.login_required
def swapactionorder():
    """Swap the order of two actions in the database.
    ---
    post:
      operationId: swapActionOrder
      description: Swap the order of two actions in the database.
      tags: [actions]
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema: SwapActionOrderContent
      responses:
        200:
          description: Action order swapped
    """
    action = Action.query.get(int(request.form.get("actionid")))
    swapaction = Action.query.get(int(request.form.get("swapid")))
    ordnum = action.ordnum
    action.ordnum = swapaction.ordnum
    swapaction.ordnum = ordnum
    db.session.commit()
    return "", 200


@api.route("/action/markasnews", methods=["POST"])
@token_auth.login_required
def markasnews():
    """Mark an action as news.
    ---
    post:
      operationId: markAsNews
      description: Mark an action as news.
      tags: [actions]
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema: MarkAsNewsContent
      responses:
        200:
          description: Action marked as news
    """
    form = MarkAsNewsForm()
    if form.validate_on_submit():
        # get action from database
        action = Action.query.get(form.actionid.data)
        if action is None:
            return bad_request("Action does not exist")

        # check if action is already marked as news
        if action.news_id:
            return bad_request("Action is already marked as news")

        # mark action as news
        news = News(
            sender_id=token_auth.current_user().id,
            sample_id=action.sample_id,
            title=form.title.data,
            content="action:{}".format(action.id),
            published=datetime.today(),
            expires=form.expires.data,
        )
        db.session.add(news)
        db.session.commit()
        action.news_id = news.id
        db.session.commit()

        news.dispatch()

        return "", 200
    elif form.is_submitted():
        return jsonify(error={field: errors for field, errors in form.errors.items()}), 400

    return "", 500  # this should never happen


@api.route("/action/unmarkasnews/<int:actionid>", methods=["POST"])
@token_auth.login_required
def unmarkasnews(actionid):
    """Unmark an action as news.
    ---
    post:
      operationId: unmarkAsNews
      description: Unmark an action as news.
      tags: [actions]
      parameters:
      - in: path
        name: actionid
        schema:
          type: integer
        required: true
        description: Numeric ID of the action to unmark as news.
      responses:
        200:
          description: Action unmarked as news
    """
    action = Action.query.get(actionid)
    if action is None:
        return bad_request("Action does not exist")

    # check if action is really marked as news
    if not action.news_id:
        return bad_request("Action is not marked as news")

    if action.news.sender != token_auth.current_user():
        return bad_request(
            "Only the sender of the news ({}) can unmark this action as news".format(
                action.news.sender.username
            ),
        )

    # by cascade deletion, this will also remove all corresponding items from the linkusernews table
    db.session.delete(action.news)

    # unmark action as news
    # TODO: record activity
    action.news_id = None
    db.session.commit()

    return "", 200

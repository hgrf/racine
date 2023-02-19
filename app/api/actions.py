from datetime import date
from flask import jsonify, request
from marshmallow import Schema, fields

from . import api
from .auth import token_auth
from .common import IdParameter, EmptySchema
from .errors import bad_request
from ..main.forms import NewActionForm

from .. import db
from ..models import Action, Sample, record_activity


class SampleParameter(Schema):
    sampleid = fields.Int()


class NewActionFormContent(Schema):
    csrf_token = fields.Str()
    timestamp = fields.Date()
    description = fields.Str()


class CreateActionError(Schema):
    resubmit = fields.Bool()


class SwapActionOrderContent(Schema):
    actionid = fields.Int()
    swapid = fields.Int()


@api.route("/action/<int:sampleid>", methods=["PUT"])
@token_auth.login_required
def createaction(sampleid):
    """Create an action in the database.
    ---
    put:
      operationId: createAction
      parameters:
      - in: path
        schema: SampleParameter
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema: NewActionFormContent
      responses:
        201:
          content:
            application/json:
              schema: EmptySchema
          description: Action created
        400:
          content:
            application/json:
              schema: CreateActionError
          description: Failed to create action
    """
    sample = Sample.query.get(sampleid)
    if (
        sample is None
        or not sample.is_accessible_for(token_auth.current_user())
        or sample.isdeleted
    ):
        return bad_request("Sample does not exist or you do not have the right to access it")

    form = NewActionForm()
    if form.validate_on_submit():
        a = Action(
            datecreated=date.today(),
            timestamp=form.timestamp.data,
            owner=token_auth.current_user(),
            sample_id=sampleid,
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
      parameters:
      - in: path
        schema: IdParameter
      responses:
        204:
          content:
            application/json:
              schema: EmptySchema
          description: Action deleted
    """
    action = Action.query.get(id)
    if action == None or not action.has_write_access(token_auth.current_user()):
        return bad_request("You do not have permission to delete this action.")
    sampleid = action.sample_id
    db.session.delete(action)
    record_activity("delete:action", token_auth.current_user(), Sample.query.get(sampleid))
    db.session.commit()
    return "", 204


@api.route("/action/swaporder", methods=["POST"])
@token_auth.login_required
def swapactionorder():  # TODO: sort out permissions for this (e.g. who has the right to change order?)
    """Swap the order of two actions in the database.
    ---
    post:
      operationId: swapActionOrder
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema: SwapActionOrderContent
      responses:
        200:
          content:
            application/json:
              schema: EmptySchema
          description: Action order swapped
    """
    action = Action.query.get(int(request.form.get("actionid")))
    swapaction = Action.query.get(int(request.form.get("swapid")))
    ordnum = action.ordnum
    action.ordnum = swapaction.ordnum
    swapaction.ordnum = ordnum
    db.session.commit()
    return "", 200

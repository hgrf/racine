from flask import jsonify
from functools import wraps
from marshmallow import fields

from . import api
from .common import OrderedSchema
from .errors import bad_request
from ..main.forms import NewSampleForm

from ..common import db
from ..models import News, Sample, Share, record_activity, token_auth
from ..models.tree import is_indirectly_shared, logical_parent


class SampleIdParameter(OrderedSchema):
    sampleid = fields.Int(metadata={"description": "Numeric ID of the sample"})


class NewSampleFormContent(OrderedSchema):
    csrf_token = fields.Str(metadata={"description": "CSRF (Cross-Site Request Forgery) token"})
    name = fields.Str(metadata={"description": "Name of the sample"})
    parent = fields.Str(metadata={"description": "Parent of the sample"})
    parentid = fields.Int(metadata={"description": "ID of the parent of the sample"})
    description = fields.Str(metadata={"description": "Description of the sample"})


def validate_sample_access(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "sampleid" not in kwargs:
            return bad_request("Invalid use of decorator: sampleid is missing")
        sample = db.session.get(Sample, kwargs.pop("sampleid"))
        if (
            sample is None
            or sample.isdeleted
            or not sample.is_accessible_for(token_auth.current_user())
        ):
            return bad_request("Sample does not exist or you do not have the right to access it.")
        return func(sample=sample, *args, **kwargs)

    return wrapper


def validate_sample_owner(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "sampleid" not in kwargs:
            return bad_request("Invalid use of decorator: sampleid is missing")
        sample = Sample.query.get(kwargs.pop("sampleid"))
        if sample is None or sample.isdeleted or sample.owner != token_auth.current_user():
            return bad_request("Sample does not exist or you do not have the right to modify it.")
        return func(sample=sample, *args, **kwargs)

    return wrapper


@api.route("/sample", methods=["PUT"])
@token_auth.login_required
def createsample():
    """Create a sample in the database.
    ---
    put:
      operationId: createSample
      description: Create a sample in the database.
      tags: [samples]
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema: NewSampleFormContent
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  sampleid:
                    type: integer
                    description: Form was not validated, but user should resubmit.
          description: Sample created
    """
    form = NewSampleForm()
    if form.validate_on_submit():
        try:
            parent_id = int(form.parentid.data) if form.parentid.data else 0
            sample = Sample(
                owner=token_auth.current_user(),
                name=form.name.data,
                parent_id=parent_id,
                description=form.description.data,
                isarchived=False,
                isdeleted=False,
            )
            db.session.add(sample)
            db.session.commit()
            record_activity("add:sample", token_auth.current_user(), sample, commit=True)
            return jsonify(sampleid=sample.id), 201
        except Exception as e:
            db.session.rollback()
            return jsonify(error={"name": [str(e)]}), 400
    elif form.is_submitted():
        error = {field: errors for field, errors in form.errors.items()}
        # workaround to get correct display of error message in FormDialog
        if "parentid" in error:
            error["parent"] = error["parentid"]
        return jsonify(error=error), 400

    return "", 500  # this should never happen


@api.route("/sample/<int:sampleid>", methods=["DELETE"])
@token_auth.login_required
@validate_sample_owner
def deletesample(sample):
    """Delete a sample from the database.
    ---
    delete:
      operationId: deleteSample
      description: Delete a sample from the database.
      tags: [samples]
      parameters:
      - in: path
        schema: SampleIdParameter
      responses:
        204:
          description: Sample deleted
    """
    record_activity("delete:sample", token_auth.current_user(), sample)
    sample.isdeleted = True  # mark sample as "deleted"
    db.session.commit()
    return "", 204


@api.route("/sample/<int:sampleid>/togglearchived", methods=["POST"])
@token_auth.login_required
@validate_sample_owner
def togglearchived(sample):
    """Toggle the isarchived-flag of a sample.
    ---
    post:
      operationId: toggleArchived
      description: Toggle the isarchived-flag of a sample.
      tags: [samples]
      parameters:
      - in: path
        schema: SampleIdParameter
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  isarchived:
                    type: boolean
          description: isarchived-flag toggled
    """
    sample.isarchived = not sample.isarchived
    db.session.commit()
    return jsonify(isarchived=sample.isarchived), 200


@api.route("/sample/<int:sampleid>/togglecollaborative", methods=["POST"])
@token_auth.login_required
@validate_sample_owner
def togglecollaborative(sample):
    """Toggle the iscollaborative-flag of a sample.
    ---
    post:
      operationId: toggleCollaborative
      description: Toggle the iscollaborative-flag of a sample.
      tags: [samples]
      parameters:
      - in: path
        schema: SampleIdParameter
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  iscollaborative:
                    type: boolean
          description: iscollaborative-flag toggled
    """
    sample.iscollaborative = not sample.iscollaborative
    db.session.commit()
    return jsonify(iscollaborative=sample.iscollaborative), 200


def recursive_news_dispatch(sample):
    affected_samples = [sample]
    while affected_samples:
        s = affected_samples.pop()
        affected_samples.extend(s.children)
        news = News.query.filter_by(sample_id=s.id).all()
        for n in news:
            n.dispatch()


@api.route("/sample/<int:sampleid>/changeparent/<int:parentid>", methods=["POST"])
@token_auth.login_required
@validate_sample_access
def changeparent(sample, parentid):
    """Change the parent of a sample.
    ---
    post:
      operationId: changeParent
      description: Change the parent of a sample.
      tags: [samples]
      parameters:
      - in: path
        schema: SampleIdParameter
      - in: path
        name: parentid
        schema:
          type: integer
      responses:
        200:
          description: parent changed
    """
    user = token_auth.current_user()

    # check if we're not trying to make the snake bite its tail
    p = Sample.query.get(parentid)
    while p:
        if p == sample:
            return bad_request("Cannot move sample")
        p = logical_parent(p, user)

    # check if the current user is the sample owner, otherwise get corresponding share
    if sample.owner != user:
        if is_indirectly_shared(sample, user):
            return bad_request(
                "The sample owner (" + sample.owner.username + ") has fixed the sample's location.",
            )

        share = Share.query.filter_by(sample=sample, user=user).first()
        if share is None:
            return bad_request("Could not find corresponding share")
        try:
            share.mountpoint_id = parentid
            db.session.commit()
        except Exception as e:
            return bad_request("Exception: " + str(e))
    else:
        # change parent ID
        try:
            sample.parent_id = parentid
            db.session.commit()

            # re-dispatch news for this sample and for all children
            recursive_news_dispatch(sample)
        except Exception as e:
            return bad_request(str(e))
    return "", 200

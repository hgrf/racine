from flask import jsonify
from marshmallow import Schema, fields

from . import api
from .common import IdParameter, EmptySchema  # noqa: F401
from .errors import bad_request
from ..main.forms import NewSampleForm

from .. import db
from ..models import News, Sample, Share, record_activity, token_auth
from ..models.tree import is_indirectly_shared, logical_parent


class NewSampleFormContent(Schema):
    csrf_token = fields.Str()
    newsamplename = fields.Str()
    newsampleparent = fields.Str()
    newsampleparentid = fields.Int()
    newsampledescription = fields.Str()


class NewSampleResponse(Schema):
    sampleid = fields.Int()


class ToggleArchivedResponse(Schema):
    isarchived = fields.Bool()


class ToggleCollaborativeResponse(Schema):
    iscollaborative = fields.Bool()


class ParentIdParameter(Schema):
    parentid = fields.Int()


@api.route("/sample", methods=["PUT"])
@token_auth.login_required
def createsample():
    """Create a sample in the database.
    ---
    put:
      operationId: createSample
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
              schema: NewSampleResponse
          description: Sample created
    """
    form = NewSampleForm()
    if form.validate_on_submit():
        try:
            parent_id = int(form.newsampleparentid.data) if form.newsampleparentid.data else 0
            sample = Sample(
                owner=token_auth.current_user(),
                name=form.newsamplename.data,
                parent_id=parent_id,
                description=form.newsampledescription.data,
                isarchived=False,
                isdeleted=False,
            )
            db.session.add(sample)
            db.session.commit()
            record_activity("add:sample", token_auth.current_user(), sample, commit=True)
            return jsonify(sampleid=sample.id), 201
        except Exception as e:
            db.session.rollback()
            return jsonify(error={"newsamplename": [str(e)]}), 400
    elif form.is_submitted():
        return jsonify(error={field: errors for field, errors in form.errors.items()}), 400

    return "", 500  # this should never happen


@api.route("/sample/<int:id>", methods=["DELETE"])
@token_auth.login_required
def deletesample(id):
    """Delete a sample from the database.
    ---
    delete:
      operationId: deleteSample
      tags: [samples]
      parameters:
      - in: path
        schema: IdParameter
      responses:
        204:
          content:
            application/json:
              schema: EmptySchema
          description: Sample deleted
    """
    sample = Sample.query.get(id)
    # TODO: put this verification in a function
    if sample is None or sample.owner != token_auth.current_user() or sample.isdeleted:
        return bad_request("You do not have permission to delete this sample.")
    record_activity("delete:sample", token_auth.current_user(), sample)
    sample.isdeleted = True  # mark sample as "deleted"
    db.session.commit()
    return "", 204


@api.route("/sample/<int:id>/togglearchived", methods=["POST"])
@token_auth.login_required
def togglearchived(id):
    """Toggle the isarchived-flag of a sample.
    ---
    post:
      operationId: toggleArchived
      tags: [samples]
      parameters:
      - in: path
        schema: IdParameter
      responses:
        200:
          content:
            application/json:
              schema: ToggleArchivedResponse
          description: isarchived-flag toggled
    """
    sample = Sample.query.get(id)
    if sample is None or sample.owner != token_auth.current_user() or sample.isdeleted:
        return bad_request("Sample does not exist or you do not have the right to access it")
    sample.isarchived = not sample.isarchived
    db.session.commit()
    return jsonify(isarchived=sample.isarchived), 200


@api.route("/sample/<int:id>/togglecollaborative", methods=["POST"])
@token_auth.login_required
def togglecollaborative(id):
    """Toggle the iscollaborative-flag of a sample.
    ---
    post:
      operationId: toggleCollaborative
      tags: [samples]
      parameters:
      - in: path
        schema: IdParameter
      responses:
        200:
          content:
            application/json:
              schema: ToggleCollaborativeResponse
          description: iscollaborative-flag toggled
    """
    sample = Sample.query.get(id)
    if sample is None or sample.owner != token_auth.current_user() or sample.isdeleted:
        return bad_request("Sample does not exist or you do not have the right to access it")
    sample.iscollaborative = not sample.iscollaborative
    db.session.commit()
    return jsonify(iscollaborative=sample.iscollaborative), 200


@api.route("/sample/<int:id>/changeparent/<int:parentid>", methods=["POST"])
@token_auth.login_required
def changeparent(id, parentid):
    """Change the parent of a sample.
    ---
    post:
      operationId: changeParent
      tags: [samples]
      parameters:
      - in: path
        schema: IdParameter
      - in: path
        schema: ParentIdParameter
      responses:
        200:
          content:
            application/json:
              schema: EmptySchema
          description: parent changed
    """
    sample = Sample.query.get(id)
    user = token_auth.current_user()
    if sample is None or not sample.is_accessible_for(user) or sample.isdeleted:
        return bad_request("Sample does not exist or you do not have the right to access it")

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
            affected_samples = [sample]
            while affected_samples:
                s = affected_samples.pop()
                affected_samples.extend(s.children)
                news = News.query.filter_by(sample_id=s.id).all()
                for n in news:
                    n.dispatch()
        except Exception as e:
            return bad_request(str(e))
    return "", 200

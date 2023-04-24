from flask import jsonify, request
from marshmallow import fields

from . import api
from .common import OrderedSchema, IdParameter, EmptySchema  # noqa: F401
from .errors import bad_request

from .. import db
from ..models import Sample, User

from ..models import News, Share, record_activity, token_auth


class CreateShareContent(OrderedSchema):
    sampleid = fields.Int()
    userid = fields.Int()
    username = fields.Str()


class CreateShareError(OrderedSchema):
    pass


@api.route("/share", methods=["PUT"])
@token_auth.login_required
def createshare():
    """Create a share in the database.
    ---
    put:
      operationId: createShare
      tags: [shares]
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema: CreateShareContent
      responses:
        201:
          content:
            application/json:
              schema: EmptySchema
          description: Share created
        400:
          content:
            application/json:
              schema: CreateShareError
          description: Failed to create share
    """
    sample = Sample.query.get(int(request.form.get("sampleid")))
    user = None
    if request.form.get("userid"):
        user = User.query.get(int(request.form.get("userid")))
    elif request.form.get("username"):
        user = User.query.filter_by(username=(request.form.get("username"))).first()
    if user is None:
        return bad_request("No valid user ID or name given")
    if sample is None or sample.owner != token_auth.current_user() or sample.isdeleted:
        return bad_request("Sample does not exist or you do not have the right to access it")
    if user in [x.user for x in sample.shares]:
        return bad_request("This share already exists")
    share = Share(sample=sample, user=user, mountpoint_id=0)
    db.session.add(share)
    record_activity("add:share", token_auth.current_user(), sample)
    db.session.commit()

    # re-dispatch news for this sample and for all children
    affected_samples = [sample]
    while affected_samples:
        s = affected_samples.pop()
        affected_samples.extend(s.children)
        news = News.query.filter_by(sample_id=s.id).all()
        for n in news:
            n.dispatch()

    return jsonify(username=user.username, userid=user.id, shareid=share.id), 201


@api.route("/share/<int:id>", methods=["DELETE"])
@token_auth.login_required
def deleteshare(id):
    """Delete a share from the database.
    ---
    delete:
      operationId: deleteShare
      tags: [shares]
      parameters:
      - in: path
        schema: IdParameter
      responses:
        204:
          content:
            application/json:
              schema: EmptySchema
          description: Share deleted
        205:
          content:
            application/json:
              schema: EmptySchema
          description: Share deleted, sample no longer accessible for current user
    """
    share = Share.query.get(id)
    if share is None or share.sample is None:
        return bad_request("Share or sample does not exist")
    if share.sample.owner != token_auth.current_user() and share.user != token_auth.current_user():
        return bad_request("You do not have the right to perform this operation")

    user = share.user

    record_activity("delete:share", token_auth.current_user(), share.sample)
    db.session.delete(share)
    db.session.commit()

    # re-dispatch news for this sample and for all children
    affected_samples = [share.sample]
    while affected_samples:
        s = affected_samples.pop()
        affected_samples.extend(s.children)
        news = News.query.filter_by(sample_id=s.id).all()
        for n in news:
            n.dispatch()

    # in this case the sample does not exist anymore for this user
    if user == token_auth.current_user():
        return "", 205

    return "", 204

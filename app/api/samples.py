from flask import jsonify
from marshmallow import Schema, fields

from . import api
from .common import IdParameter, EmptySchema
from .errors import bad_request
from ..main.forms import NewSampleForm

from .. import db
from ..models import Sample, record_activity, token_auth


class NewSampleFormContent(Schema):
    csrf_token = fields.Str()
    newsamplename = fields.Str()
    newsampleparent = fields.Str()
    newsampleparentid = fields.Int()
    newsampledescription = fields.Str()


class NewSampleResponse(Schema):
    sampleid = fields.Int()


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

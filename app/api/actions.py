from . import api
from .auth import token_auth
from .errors import bad_request

from .. import db

from ..models import Action, Sample, record_activity


from marshmallow import Schema, fields


class IdParameter(Schema):
    id = fields.Int()


class EmptySchema(Schema):
    pass


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

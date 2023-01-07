from . import api
from .auth import token_auth
from .errors import bad_request

from .. import db

from ..models import Action, Sample, record_activity


@api.route("/action/<int:id>", methods=["DELETE"])
@token_auth.login_required
def deleteaction(id):
    action = Action.query.get(id)
    if action == None or not action.has_write_access(token_auth.current_user()):
        return bad_request("You do not have permission to delete this action.")
    sampleid = action.sample_id
    db.session.delete(action)
    record_activity("delete:action", token_auth.current_user(), Sample.query.get(sampleid))
    db.session.commit()
    return "", 204

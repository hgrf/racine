from . import api
from .auth import token_auth
from .errors import bad_request

from .. import db

from ..models import Sample, record_activity


@api.route("/sample/<int:id>", methods=["DELETE"])
@token_auth.login_required
def deletesample(id):
    sample = Sample.query.get(id)
    # TODO: put this verification in a function
    if sample is None or sample.owner != token_auth.current_user() or sample.isdeleted:
        return bad_request("You do not have permission to delete this sample.")
    record_activity("delete:sample", token_auth.current_user(), sample)
    sample.isdeleted = True  # mark sample as "deleted"
    db.session.commit()
    return "", 204

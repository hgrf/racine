from . import api
from .auth import token_auth
from .errors import bad_request

from .. import db

from ..models import News, Share, record_activity


@api.route("/share/<int:id>", methods=["DELETE"])
@token_auth.login_required
def deleteshare(id):
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

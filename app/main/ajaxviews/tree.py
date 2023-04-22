from flask import request, render_template
from flask_login import current_user, login_required

from .. import main
from ...models import User, Sample


@main.route("/tree", methods=["GET"])
@login_required
def tree():
    inheritance = User.query.filter_by(heir=current_user).all()
    showarchived = (
        True
        if request.args.get("showarchived") is not None
        and request.args.get("showarchived") == "true"
        else False
    )
    order = request.args.get("order") if request.args.get("order") else "id"

    # only query root level samples, the template will build the hierarchy
    samples = Sample.query.filter_by(owner=current_user, parent_id=0, isdeleted=False).all()
    samples.extend(current_user.directshares)

    return render_template(
        "main/tree.html",
        samples=samples,
        inheritance=inheritance,
        showarchived=showarchived,
        order=order,
    )

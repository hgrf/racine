from flask import abort, request, render_template
from flask_login import current_user, login_required

from . import ajaxviews
from ...models import User, build_tree


@ajaxviews.route("/tree", methods=["GET"])
@login_required
def tree():
    if request.args.get("order") not in ["id", "name", "last_modified"]:
        abort(400)
    if request.args.get("showarchived") not in ["true", "false"]:
        abort(400)

    order = request.args.get("order")
    showarchived = request.args.get("showarchived") == "true"

    return render_template(
        "main/tree.html",
        root=build_tree(current_user, order=order),
        inheritance=User.query.filter_by(heir=current_user).all(),
        showarchived=showarchived,
        order=order,
    )

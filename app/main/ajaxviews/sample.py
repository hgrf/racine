from datetime import date
from flask import current_app as app
from flask import jsonify, request, render_template
from flask_login import current_user, login_required

from . import ajaxviews
from ..forms import NewActionForm
from ...models import Action, Sample


@ajaxviews.route("/editor/<sampleid>", methods=["GET", "POST"])
@login_required
def editor(sampleid):
    sample = Sample.query.get(sampleid)
    shares = sample.shares if sample is not None else []
    showparentactions = request.args.get("showparentactions") == "true"
    invertactionorder = request.args.get("invertactionorder") == "true"

    if sample is None or not sample.is_accessible_for(current_user) or sample.isdeleted:
        return jsonify(error="Sample not found"), 404
    else:
        form = NewActionForm()
        form.description.data = ""
        form.timestamp.data = date.today()

        # get actions for this sample and all parent samples and order them by ordnum
        actions = []
        s = sample
        while s is not None:
            actions.extend(Action.query.filter_by(sample=s).order_by(Action.ordnum).all())
            s = s.parent
            if not showparentactions:
                break
        actions = sorted(actions, key=lambda a: a.ordnum, reverse=invertactionorder)

        return render_template(
            "main/sample.html",
            icons=app.config["ICONS"],
            sample=sample,
            actions=actions,
            newactionform=form,
            shares=shares,
            showparentactions=showparentactions,
            invertactionorder=invertactionorder,
        )

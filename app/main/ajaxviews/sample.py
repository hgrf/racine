from datetime import date
from flask import request, render_template
from flask_login import current_user, login_required

from .. import main
from ..forms import NewActionForm
from ...models import Action, Sample


@main.route("/editor/<sampleid>", methods=["GET", "POST"])
@login_required
def editor(sampleid):
    sample = Sample.query.get(sampleid)
    shares = sample.shares
    showparentactions = (
        True
        if request.args.get("showparentactions") is not None
        and request.args.get("showparentactions") == "true"
        else False
    )
    invertactionorder = (
        True
        if request.args.get("invertactionorder") is not None
        and request.args.get("invertactionorder") == "true"
        else False
    )

    if sample is None or not sample.is_accessible_for(current_user) or sample.isdeleted:
        return render_template("errors/404.html"), 404
    else:
        form = NewActionForm()
        form.description.data = ""
        form.timestamp.data = date.today()

        # ----- get actions for this sample and all parent samples and order them by ordnum
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
            sample=sample,
            actions=actions,
            form=form,
            shares=shares,
            showparentactions=showparentactions,
            invertactionorder=invertactionorder,
        )

from flask import render_template
from . import printdata
from ..models import Sample, list_tree
from .forms import RequestActionsForm
from flask_login import login_required, current_user


@printdata.route("/", methods=["GET", "POST"])
@login_required
def overview():
    form = RequestActionsForm()
    actions = []
    if form.validate_on_submit():
        if form.sampleid.data:
            sample = Sample.query.get(int(form.sampleid.data))
            samples = [sample] if sample else []
        else:
            samples = list_tree(current_user)

        for s in samples:
            for a in s.actions:
                if form.datefrom.data and a.timestamp and a.timestamp < form.datefrom.data:
                    continue
                if form.dateto.data and a.timestamp and a.timestamp > form.dateto.data:
                    continue
                actions.append(a)
        actions = sorted(actions, key=lambda x: x.ordnum)
        actions = sorted(actions, key=lambda x: x.sample_id)
    return render_template(
        "print.html",
        form=form,
        actions=actions,
        sampleerror=True if form.sampleid.data == "-1" else False,
    )

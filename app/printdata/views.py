from flask import render_template
from . import printdata
from ..models import Sample
from .forms import RequestActionsForm
from flask_login import login_required, current_user


@printdata.route("/", methods=["GET", "POST"])
@login_required
def overview():
    form = RequestActionsForm()
    actions = []
    if form.validate_on_submit():
        sampleid = int(form.sampleid.data) if form.sampleid.data else 0

        # TODO: both this tree function and the below samples.extend... are somewhat duplicated
        #       in main/views.py (e.g. in search() and in navbar()) and should be in a
        #       separate function
        def tree(samples):
            result = []
            for s in samples:
                result.append(s)
                # TODO: does s.children contain deleted samples ?
                result.extend(tree(s.children + s.mountedsamples))
            return result

        samples = Sample.query.filter_by(owner=current_user, parent_id=0, isdeleted=False).all()
        samples.extend(current_user.directshares)
        all_samples = tree(samples)

        actions = []
        for s in all_samples:
            if sampleid and sampleid != s.id:
                continue
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

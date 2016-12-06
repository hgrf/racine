from flask import render_template, redirect, request, url_for
from . import printdata
from .. import db
from ..models import Action, Sample
from forms import RequestActionsForm
from flask.ext.login import login_required, current_user

from datetime import date
from datetime import datetime


@printdata.route('/', methods=['GET', 'POST'])
@login_required
def overview():
    form = RequestActionsForm()
    actions = []
    if form.validate_on_submit():
        try: datefrom = datetime.strptime(form.datefrom.data, "%Y-%m-%d")
        except ValueError: datefrom = None
        try: dateto = datetime.strptime(form.dateto.data, "%Y-%m-%d")
        except ValueError: dateto = None
        query = Action.query.join(Action.sample).filter(Sample.owner == current_user)
        if datefrom:
            query = query.filter(Action.timestamp >= datefrom)
        if dateto:
            query = query.filter(Action.timestamp <= dateto)
        if form.sample.data:
            query = query.filter(Sample.name == form.sample.data)
        actions = query.order_by(Action.sample_id, Action.ordnum)
    return render_template('print.html', form=form, actions=actions)
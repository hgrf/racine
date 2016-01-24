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
        actions = Action.query.join(Action.sample).filter(Action.timestamp >= form.datefrom.data, Action.timestamp <= form.dateto.data, Sample.owner == current_user)
    return render_template('print.html', form=form, actions=actions)
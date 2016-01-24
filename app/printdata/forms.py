from flask.ext.wtf import Form
from wtforms import SubmitField
from wtforms.fields.html5 import DateField


class RequestActionsForm(Form):
    datefrom = DateField('From:')
    dateto = DateField('To:')
    submit = SubmitField('Submit')

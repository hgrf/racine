from flask.ext.wtf import Form
from wtforms import SubmitField, StringField

class RequestActionsForm(Form):
    datefrom = StringField('From:')
    dateto = StringField('To:')
    sample = StringField('Sample:')
    submit = SubmitField('Submit')

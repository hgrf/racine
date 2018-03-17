from flask.ext.wtf import Form
from wtforms import SubmitField, StringField, HiddenField

class RequestActionsForm(Form):
    datefrom = StringField('From:')
    dateto = StringField('To:')
    sample = StringField('Sample:')
    sampleid = HiddenField()
    submit = SubmitField('Submit')

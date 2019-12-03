from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, HiddenField


class RequestActionsForm(FlaskForm):
    datefrom = StringField('From:')
    dateto = StringField('To:')
    sample = StringField('Sample:')
    sampleid = HiddenField()
    submit = SubmitField('Submit')

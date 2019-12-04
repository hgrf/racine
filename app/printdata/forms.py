from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, HiddenField


class RequestActionsForm(FlaskForm):
    datefrom = StringField('From:', render_kw={"placeholder": "yyyy-mm-dd"})
    dateto = StringField('To:', render_kw={"placeholder": "yyyy-mm-dd"})
    sample = StringField('Sample:')
    sampleid = HiddenField()
    submit = SubmitField('Submit')

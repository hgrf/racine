from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField, HiddenField
from wtforms.fields.html5 import DateField
from ..validators import ValidSampleName


class NewActionForm(FlaskForm):
    timestamp = DateField('Date:')
    description = TextAreaField('Description:')
    submit = SubmitField('Submit')


class NewSampleForm(FlaskForm):
    name = StringField('Sample name:', validators=[ValidSampleName()])
    parent = StringField('Parent:')
    parentid = HiddenField()
    description = TextAreaField('Description:')
    submit = SubmitField('Submit')


class NewMatrixForm(FlaskForm):
    height = StringField('Height:')  # use some sort of integer field here!
    width = StringField('Width:')  # use some sort of integer field here!
    submit = SubmitField('Submit')

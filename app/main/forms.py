from flask.ext.wtf import Form
from wtforms import SubmitField, TextAreaField, StringField, HiddenField
from wtforms.fields.html5 import DateField
from ..validators import ValidSampleName


class NewActionForm(Form):
    timestamp = DateField('Date:')
    description = TextAreaField('Description:')
    submit = SubmitField('Submit')


class NewSampleForm(Form):
    name = StringField('Sample name:', validators=[ValidSampleName()])
    parent = StringField('Parent:')
    parentid = HiddenField()
    description = TextAreaField('Description:')
    submit = SubmitField('Submit')


class NewMatrixForm(Form):
    height = StringField('Height:')  # use some sort of integer field here!
    width = StringField('Width:')  # use some sort of integer field here!
    submit = SubmitField('Submit')
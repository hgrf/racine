from flask.ext.wtf import Form
from wtforms import SubmitField, TextAreaField, StringField, HiddenField
from wtforms.fields.html5 import DateField
from wtforms.validators import Regexp


class NewActionForm(Form):
    timestamp = DateField('Date:')
    description = TextAreaField('Description:')
    submit = SubmitField('Submit')


class NewSampleForm(Form):
    name = StringField('Sample name:', validators=[Regexp('^(?! ).+', 0, 'Sample names must not start with a space.')])
    parent = StringField('Parent:')
    parentid = HiddenField()
    description = TextAreaField('Description:')
    submit = SubmitField('Submit')


class NewMatrixForm(Form):
    height = StringField('Height:')  # use some sort of integer field here!
    width = StringField('Width:')  # use some sort of integer field here!
    submit = SubmitField('Submit')
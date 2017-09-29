from flask.ext.wtf import Form
from wtforms import SelectField, SubmitField, TextAreaField, StringField
from wtforms.fields.html5 import DateField


class NewActionForm(Form):
    timestamp = DateField('Date:')
    description = TextAreaField('Description:')
    submit = SubmitField('Submit')


class NewSampleForm(Form):
    name = StringField('Sample name:')
    parent = SelectField('Parent:', coerce=int)
    description = TextAreaField('Description:')
    submit = SubmitField('Submit')


class NewMatrixForm(Form):
    height = StringField('Height:')  # use some sort of integer field here!
    width = StringField('Width:')  # use some sort of integer field here!
    submit = SubmitField('Submit')
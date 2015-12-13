from flask.ext.wtf import Form
from wtforms import SelectField, SubmitField, TextAreaField, StringField
from wtforms.widgets import TextArea
from wtforms.fields.html5 import DateField


class NewActionForm(Form):
    timestamp = DateField('Date:')
    actiontype = SelectField('Action type:', coerce=int)
    description = TextAreaField('Description:')
    submit = SubmitField('Submit')


class NewSampleForm(Form):
    name = StringField('Sample name:')
    parent = SelectField('Parent:', coerce=int)
    sampletype = SelectField('Sample type:', coerce=int)
    submit = SubmitField('Submit')


class NewTypeForm(Form):
    name = StringField('Type name:')
    submit = SubmitField('Submit')


class NewMatrixForm(Form):
    height = StringField('Height:')  # use some sort of integer field here!
    width = StringField('Width:')  # use some sort of integer field here!
    submit = SubmitField('Submit')


class NewSMBResourceForm(Form):
    name = StringField('SMB Resource name:')
    servername = StringField('Server name (NetBIOS):')
    serveraddr = StringField('Server address:')
    sharename = StringField('Share name:')
    userid = StringField('User name:')
    password = StringField('Password:')
    submit = SubmitField('Submit')


class ShutdownForm(Form):
    submit = SubmitField('Confirm shutdown')
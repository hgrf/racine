from flask.ext.wtf import Form
from wtforms import SubmitField, StringField


class NewTypeForm(Form):
    name = StringField('Type name:')
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
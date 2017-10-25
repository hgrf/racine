from flask.ext.wtf import Form
from wtforms import SubmitField, StringField, ValidationError, PasswordField, BooleanField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from ..models import User


class NewTypeForm(Form):
    name = StringField('Type name:')
    submit = SubmitField('Submit')


class NewSMBResourceForm(Form):
    name = StringField('SMB Resource name:')
    servername = StringField('Server name (NetBIOS):')
    serveraddr = StringField('Server address:')
    sharename = StringField('Share name:')
    path = StringField('Path:')
    userid = StringField('User name:')
    password = StringField('Password:')
    submit = SubmitField('Submit')


class ShutdownForm(Form):
    submit = SubmitField('Confirm shutdown')


class NewUserForm(Form):
    is_admin = BooleanField('Admin:')
    username = StringField('User name:', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_. ]*$', 0,
'Usernames must contain only letters, numbers, dots, underscores or spaces and start with a letter.')])
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
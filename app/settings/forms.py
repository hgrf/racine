from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, ValidationError, PasswordField, BooleanField, IntegerField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, DataRequired
from ..models import User


class NewSMBResourceForm(FlaskForm):
    name = StringField('SMB Resource name:')
    servername = StringField('Server name (NetBIOS):')
    serveraddr = StringField('Server address:')
    sharename = StringField('Share name:')
    path = StringField('Path:')
    userid = StringField('User name:')
    password = StringField('Password:')
    submit = SubmitField('Submit')


class ShutdownForm(FlaskForm):
    submit = SubmitField('Confirm shutdown')


class NewUserForm(FlaskForm):
    is_admin = BooleanField('Admin')
    username = StringField('User name', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_. ]*$', 0,
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


class EmailSettings(FlaskForm):
    sender = StringField('Sender:', validators=[DataRequired()])
    server = StringField('Server:', validators=[DataRequired()])
    port = IntegerField('Port:', validators=[DataRequired()])
    use_ssl = BooleanField('Use SSL')
    use_tls = BooleanField('Use TLS')
    username = StringField('User name:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Save changes and send test email')
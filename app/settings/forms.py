from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from ..main.forms import APIForm
from ..validators import email_already_registered, username_already_registered


class NewSMBResourceForm(FlaskForm):
    name = StringField("SMB Resource name:")
    servername = StringField("Server name (NetBIOS):")
    serveraddr = StringField("Server address:")
    serverport = IntegerField("Server port:")
    domainname = StringField("Domain:")
    sharename = StringField("Share name:")
    path = StringField("Path:")
    userid = StringField("User name:")
    password = PasswordField("Password:")
    submit = SubmitField("Submit")


class NewUserForm(APIForm):
    _prfx = "new-user-"

    is_admin = BooleanField("Admin")
    username = StringField(
        "User name",
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_. ]*$",
                0,
                "User names must contain only letters, numbers, dots, "
                + "underscores or spaces and start with a letter.",
            ),
            username_already_registered,
        ],
    )
    email = StringField(
        "Email", validators=[DataRequired(), Length(1, 64), Email(), email_already_registered]
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), EqualTo("password2", message="Passwords must match.")],
    )
    password2 = PasswordField("Confirm password", validators=[DataRequired()])


class EmailSettings(FlaskForm):
    sender = StringField("Sender:", validators=[DataRequired()])
    server = StringField("Server:", validators=[DataRequired()])
    port = IntegerField("Port:", validators=[DataRequired()])
    use_ssl = BooleanField("Use SSL")
    use_tls = BooleanField("Use TLS")
    username = StringField("User name:")
    password = PasswordField("Password:")
    submit = SubmitField("Save changes and send test email")


class UsageStatsSettings(FlaskForm):
    key = StringField("Key:", validators=[DataRequired()], render_kw={"readonly": True})
    site = StringField("Site name:", validators=[DataRequired()])
    submit = SubmitField("Save changes")

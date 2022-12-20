from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, StringField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, ValidationError
from flask_login import current_user
from ..models import User


class ChangePasswordForm(FlaskForm):
    oldpassword = PasswordField("Old password")
    password = PasswordField(
        "New password",
        validators=[DataRequired(), EqualTo("password2", message="Passwords must match.")],
    )
    password2 = PasswordField("Confirm new password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ChangeDetailsForm(FlaskForm):
    username = StringField(
        "User name:",
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_. ]*$",
                0,
                "User names must start with a letter  "
                + "and contain only letters, numbers, underscores, fullstops or spaces.",
            ),
        ],
    )
    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField("Enter password", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def validate_email(self, field):
        if field.data != current_user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")

    def validate_username(self, field):
        if (
            field.data != current_user.username
            and User.query.filter_by(username=field.data).first()
        ):
            raise ValidationError("Username already in use.")

    def validate_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError("Password incorrect.")

from wtforms.validators import ValidationError
from .models import User


def email_already_registered(form, field):
    if User.query.filter_by(email=field.data).first():
        raise ValidationError('Email already registered.')


def username_already_registered(form, field):
    if User.query.filter_by(username=field.data).first():
        raise ValidationError('Username already in use.')


def validate_form_field(form, field, value):
    field = getattr(form, field)
    field.data = value
    if field.validate(form):
        return value
    else:
        raise Exception(field.errors[0])

from flask.ext.wtf import Form
from wtforms import SelectField, SubmitField, TextAreaField, StringField, PasswordField
from wtforms.validators import Required, EqualTo
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
    description = TextAreaField('Description:')
    submit = SubmitField('Submit')


class NewMatrixForm(Form):
    height = StringField('Height:')  # use some sort of integer field here!
    width = StringField('Width:')  # use some sort of integer field here!
    submit = SubmitField('Submit')


class ChangePasswordForm(Form):
    oldpassword = PasswordField('Old password')
    password = PasswordField('New password', validators=[Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm new password', validators=[Required()])
    submit = SubmitField('Submit')
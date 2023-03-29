from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField, HiddenField, ValidationError, DateField
from wtforms.validators import Length, Regexp
from ..models import Sample, SAMPLE_NAME_LENGTH


class NewActionForm(FlaskForm):
    timestamp = DateField("Date:", format="%Y-%m-%d", render_kw={"placeholder": "yyyy-mm-dd"})
    description = TextAreaField("Description:")
    submit = SubmitField("Submit")


class NewSampleForm(FlaskForm):
    newsamplename = StringField(
        "Sample name:",
        validators=[
            Length(1, SAMPLE_NAME_LENGTH),
            Regexp("^(?! .*$).*", 0, "Sample name must not start with space."),
        ],
    )
    newsampleparent = StringField("Parent:")
    newsampleparentid = HiddenField()
    newsampledescription = TextAreaField("Description:")

    def validate_newsampleparentid(self, field):
        parentid = int(field.data) if field.data else 0
        if parentid and not Sample.query.get(parentid):
            raise ValidationError("Please select a valid parent sample or leave that field empty.")


class MarkActionAsNewsForm(FlaskForm):
    title = StringField("Title:")
    expires = DateField("Expires:", format="%Y-%m-%d", render_kw={"placeholder": "yyyy-mm-dd"})

    actionid = HiddenField()

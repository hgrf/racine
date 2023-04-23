from flask_wtf import FlaskForm
from werkzeug.datastructures import ImmutableMultiDict
from wtforms import SubmitField, TextAreaField, StringField, HiddenField, ValidationError, DateField
from wtforms.validators import Length, Regexp
from ..models import Sample, SAMPLE_NAME_LENGTH


class APIForm(FlaskForm):
    # add customizable prefix to avoid name collisions with other forms
    _prfx = "api-form-"

    def __init__(self):
        super(APIForm, self).__init__(prefix=self._prfx)

    def process(self, formdata=None, *args, **kwargs):
        formdata = self.meta.wrap_formdata(self, formdata)
        if isinstance(formdata, ImmutableMultiDict):
            # add prefix before passing to base class
            formdata = ImmutableMultiDict([(self._prfx + k, v) for k, v in formdata.items()])
        return super(APIForm, self).process(formdata, *args, **kwargs)


class NewActionForm(APIForm):
    _prfx = "new-action-"

    timestamp = DateField("Date:", format="%Y-%m-%d", render_kw={"placeholder": "yyyy-mm-dd"})
    description = TextAreaField("Description:")
    submit = SubmitField("Submit")


class NewSampleForm(APIForm):
    _prfx = "new-sample-"

    name = StringField(
        "Sample name:",
        validators=[
            Length(1, SAMPLE_NAME_LENGTH),
            Regexp("^(?! .*$).*", 0, "Sample name must not start with space."),
        ],
    )
    parent = StringField("Parent:")
    parentid = HiddenField()
    description = TextAreaField("Description:")

    def validate_parentid(self, field):
        parentid = int(field.data) if field.data else 0
        if parentid and not Sample.query.get(parentid):
            raise ValidationError("Please select a valid parent sample or leave that field empty.")


class MarkAsNewsForm(APIForm):
    _prfx = "mark-as-news-"

    title = StringField("Title:")
    expires = DateField("Expires:", format="%Y-%m-%d", render_kw={"placeholder": "yyyy-mm-dd"})

    actionid = HiddenField()

from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, HiddenField, DateField, validators


class RequestActionsForm(FlaskForm):
    datefrom = DateField(
        "From:",
        format="%Y-%m-%d",
        render_kw={"placeholder": "yyyy-mm-dd"},
        validators=(validators.Optional(),),
    )
    dateto = DateField(
        "To:",
        format="%Y-%m-%d",
        render_kw={"placeholder": "yyyy-mm-dd"},
        validators=(validators.Optional(),),
    )
    sample = StringField("Sample:")
    sampleid = HiddenField()
    submit = SubmitField("Submit")

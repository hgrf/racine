from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField, HiddenField, ValidationError
from wtforms.validators import Length, Regexp
from wtforms.fields.html5 import DateField
from ..models import Sample, SAMPLE_NAME_LENGTH


class NewActionForm(FlaskForm):
    timestamp = DateField('Date:')
    description = TextAreaField('Description:')
    submit = SubmitField('Submit')


class NewSampleForm(FlaskForm):
    newsamplename = StringField('Sample name:', validators=[Length(1, SAMPLE_NAME_LENGTH),
                                                            Regexp('^(?! .*$).*', 0,
                                                            'Sample name must not start with space.')])
    newsampleparent = StringField('Parent:')
    newsampleparentid = HiddenField()
    newsampledescription = TextAreaField('Description:')

    def validate_newsampleparentid(self, field):
        parentid = int(field.data) if field.data else 0
        if parentid and not Sample.query.get(parentid):
            raise ValidationError('Please select a valid parent sample or leave that field empty.')

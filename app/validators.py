from wtforms.validators import ValidationError
from models import SAMPLE_NAME_LENGTH

class ValidSampleName(object):
    def __init__(self):
        pass

    @staticmethod
    def validate(name):
        if len(name) > SAMPLE_NAME_LENGTH:
            raise ValidationError('Name too long.')
        if name[0] == ' ':
            raise ValidationError('Name must not start with a space.')
        # TODO: check here if user already has a sample with this name in this hierarchy level
        #     if Sample.query.filter_by(owner=current_user, name=name).first() is not None:

        return name

    def __call__(self, form, field):
        self.validate(field.data)

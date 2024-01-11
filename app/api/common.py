from marshmallow import Schema


class OrderedSchema(Schema):
    class Meta:
        ordered = True

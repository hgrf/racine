from marshmallow import Schema, fields


class OrderedSchema(Schema):
    class Meta:
        ordered = True


class IdParameter(OrderedSchema):
    id = fields.Int()


class EmptySchema(OrderedSchema):
    pass

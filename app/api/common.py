from marshmallow import Schema, fields


class IdParameter(Schema):
    id = fields.Int()


class EmptySchema(Schema):
    pass

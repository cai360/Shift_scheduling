from marshmallow import Schema, fields, validate

class UserCreateSchema(Schema):

    username = fields.String(required=True)
    email = fields.Email(required=True)
    hash = fields.String(required=True, validate=validate.Length(min=8))

class UserOutchema(Schema):
    id = fields.Integer()
    username = fields.String()
    email = fields.Email()
    active = fields.Boolean()
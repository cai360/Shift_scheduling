from marshmallow import Schema, fields, validate

class UserCreateSchema(Schema):
    username = fields.String(required=True)
    email = fields.Email(required=True)
    hash = fields.String(required=True, validate=validate.Length(min=8))

class UserUpdateSchema(Schema):
    username = fields.String(required=False)
    email = fields.Email(required=False)
    active = fields.Boolean(required=False, load_default=True)

class UserOutSchema(Schema):
    id = fields.Integer()
    username = fields.String()
    email = fields.Email()
    active = fields.Boolean()
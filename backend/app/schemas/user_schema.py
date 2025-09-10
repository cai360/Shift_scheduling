from marshmallow import Schema, fields, validate
from marshmallow.validate import Length

class UserCreateSchema(Schema):
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8), load_only=True)

class UserUpdateSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=False)
    email = fields.Email(required=False)
    active = fields.Boolean(required=False, load_default=True)

class UserOutSchema(Schema):
    id = fields.Integer()
    username = fields.String()
    email = fields.Email()
    active = fields.Boolean()


class UserUpdatePassword(Schema):
    id = fields.Integer(required = True)
    password = fields.String(load_only=True, required = True)


class LoginSchema(Schema):
    email = fields.Email(required=False)
    password = fields.String(required=True, load_only=True, validate=Length(min=8))


class TokenOutSchema(Schema):
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)


from marshmallow import Schema, fields, validate
from marshmallow.validate import Length

class LoginEmailSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=Length(min=8))


class TokenOutSchema(Schema):
    access_token = fields.Str(required=True)
    refresh_token = fields.Str(required=True)
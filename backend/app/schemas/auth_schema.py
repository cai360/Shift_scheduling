from marshmallow import Schema, fields, validate

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        load_only=True
    )

class TokenOutSchema(Schema):
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)

class RefreshSchema(Schema):
    refresh_token = fields.String(required=True)
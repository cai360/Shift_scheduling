from marshmallow import Schema, fields, validate
from marshmallow.validate import Length

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        load_only=True
    )

class TokenOutSchema(Schema):
    """Schema for returning JWT tokens after login/refresh."""
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)

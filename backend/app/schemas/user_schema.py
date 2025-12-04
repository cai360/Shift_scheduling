from marshmallow import Schema, fields, validate

class UserCreateSchema(Schema):
    username = fields.String(
        required=True,
        validate=validate.Length(min=2, max=64)
    )
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=8)
    )
class UserUpdateSchema(Schema):
    username = fields.String(required=False, validate=validate.Length(min=2, max=64))
    email = fields.Email(required=False)

class UserUpdatePasswordSchema(Schema):
    id = fields.UUID(required=True)
    password = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=8)
    )

class UserOutSchema(Schema):
    id = fields.UUID(dump_only=True)
    username = fields.String()
    email = fields.Email()

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
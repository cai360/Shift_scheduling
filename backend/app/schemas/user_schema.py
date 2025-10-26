from marshmallow import Schema, fields, validate
from marshmallow.validate import Length

class UserCreateSchema(Schema):
    username = fields.String(
        required=True,
        validate=Length(min=2, max=64),
        description="Username must be between 2 and 64 characters."
    )
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        load_only=True,
        validate=Length(min=8),
        description="Password must be at least 8 characters long."
    )
class UserUpdateSchema(Schema):
    username = fields.String(required=False, validate=Length(min=2, max=64))
    email = fields.Email(required=False)
    active = fields.Boolean(required=False)

class UserUpdatePasswordSchema(Schema):
    id = fields.Integer(required=True)
    password = fields.String(
        required=True,
        load_only=True,
        validate=Length(min=8),
        description="New password must be at least 8 characters long."
    )

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        load_only=True,
        validate=Length(min=8)
    )

class TokenOutSchema(Schema):
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)


class CompanyMembershipSchema(Schema):
    company_id = fields.Integer()
    company_name = fields.String(attribute="company.name")
    role = fields.String()
    is_active = fields.Boolean()
    joined_at = fields.DateTime()

class UserOutSchema(Schema):
    id = fields.Integer()
    username = fields.String()
    email = fields.Email()
    active = fields.Boolean()
    memberships = fields.List(
        fields.Nested(CompanyMembershipSchema),
        attribute="company_memberships"
    )
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
from marshmallow import Schema, fields, validate

class CompanyUserOutSchema(Schema):
    user_id = fields.UUID()
    role = fields.String()
    username = fields.Method("get_username")
    email = fields.Method("get_email")

    def get_username(self, obj):
        return obj.user.username if obj.user else None
    
    def get_email(self, obj):
        return obj.user.email if obj.user else None
    

class UpdateRoleSchema(Schema):
    role = fields.String(
        required=True,
        validate=validate.OneOf(["manager", "employee"]),
    )

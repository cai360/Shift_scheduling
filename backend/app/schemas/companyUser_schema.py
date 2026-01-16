from marshmallow import Schema, fields

class CompanyUserOutSchema(Schema):
    user_id = fields.UUID()
    role = fields.String()
    user = fields.Nested("UserOutSchema")
    created_at = fields.DateTime(dump_only=True)

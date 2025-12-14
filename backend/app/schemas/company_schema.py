from marshmallow import Schema, fields
from marshmallow.validate import Length

class CompanyCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String(allow_none=True)
    is_active = fields.Boolean(required=False)

class CompanyUpdateSchema(Schema):
    name = fields.String(required=False)
    description = fields.String(allow_none=True, required=False)
    is_active = fields.Boolean(required=False)

class CompanyOutSchema(Schema):
    id = fields.UUID()
    name = fields.String()
    description = fields.String(allow_none=True)
    is_active = fields.Boolean()
    deleted_at = fields.DateTime(allow_none=True)  
    created_at = fields.DateTime()
    updated_at = fields.DateTime()



from marshmallow import Schema, fields
from marshmallow.validate import Length

class CompanyCreateSchema(Schema):
    name = fields.String(required=True )
    description = fields.String(required = False, allow_none=True)
    required_swap_approval = fields.Boolean(required=False)
    is_active = fields.Boolean(required=False)

class CompanyUpdateScehma(Schema):
    name = fields.String(required=True)
    description = fields.String(required=False, allow_none=True)
    required_swap_approval = fields.Boolean(required=False)
    is_active = fields.Boolean(required=False)

class CompanyOutSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    description = fields.String(allow_none=True)
    require_swap_approval = fields.Boolean()
    is_active = fields.Boolean()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()





from marshmallow import Schema, fields
from marshmallow.validate import Length


class UnavailabilityCreateSchema(Schema):
    start_at = fields.DateTime(required=True)
    end_at = fields.DateTime(required=True)

class UnavailabilityUpdateSchema(Schema):
    start_at = fields.DateTime(required=True)
    end_at = fields.DateTime(required=True)

class UnavailabilityOutSchema(Schema):
    id = fields.UUID()
    user_id = fields.UUID(required=True)
    company_id = fields.UUID(required=True)
    start_at = fields.DateTime(required=True)
    end_at = fields.DateTime(required=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)

class UnavailabilityListOutSchema(Schema):
    id = fields.UUID()
    user_id = fields.UUID(required=True)
    company_id = fields.UUID(required=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
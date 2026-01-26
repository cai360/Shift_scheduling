from marshmallow import Schema, fields, validates_schema
from marshmallow.validate import Length


class UnavailabilityCreateSchema(Schema):
    start_at = fields.DateTime(required=True)
    end_at = fields.DateTime(required=True)

    @validates_schema
    def validate_date_range(self, data, **kwargs):
        if data["start_at"] > data["end_at"]:
            raise ValueError("end_at must be after start_at.")

class UnavailabilityUpdateSchema(Schema):
    start_at = fields.DateTime(required=True)
    end_at = fields.DateTime(required=True)
    
    @validates_schema
    def validate_date_range(self, data, **kwargs):
        if data["start_at"] > data["end_at"]:
            raise ValueError("end_at must be after start_at.")

class UnavailabilityOutSchema(Schema):
    id = fields.UUID()
    user_id = fields.UUID(required=True)
    company_id = fields.UUID(required=True)
    start_at = fields.DateTime(required=True)
    end_at = fields.DateTime(required=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
    deleted_at = fields.DateTime(required=None)
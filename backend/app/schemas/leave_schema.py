from marshmallow import (Schema, fields, validate, validates_schema, ValidationError)
from sqlalchemy.dialects.postgresql import UUID

class LeaveCreateSchema(Schema):

    start_date = fields.Date(required=True) #yyyy-mm-dd
    end_date = fields.Date(required=True)

    start_time = fields.Time(required=True) ##hh:mm
    end_time = fields.Time(required=True)

    type = fields.String(required=True)
    
    reason = fields.String(required=True)

    reviewed_by = fields.UUID(required=True)

    @validates_schema
    def validate_date_range(self, data, **kwargs):
        if data["start_date"] > data["end_date"]:
            raise ValidationError(
                "start_date must be before or equal to end_date"
            )

        
class LeaveOutSchema(Schema):
    id = fields.UUID(dump_only=True)
    company_id = fields.UUID(dump_only=True)

    start_date = fields.DateTime(dump_only=True)
    end_date = fields.DateTime(dump_only=True)

    status = fields.String(dump_only=True)
    type = fields.String(dump_only=True, required=True, validate=validate.OneOf(["sick", "annual", "personal"]))
    reason = fields.String(dump_only=True)

    reviewed_at = fields.DateTime(dump_only=True, allow_none=True)
    reviewed_by = fields.UUID(dump_only=True, allow_none=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True, allow_none=True)


class LeaveReviewSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf(["pending","approved", "rejected", "withdrawn"]))
    reject_reason = fields.String(allow_none=True)

class LeaveUpdateSchema(Schema):
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

    type = fields.String(required=True)
    reason = fields.String(required=True)

    reviewed_by = fields.UUID(required=True)

    @validates_schema
    def validate_date_range(self, data, **kwargs):
        if data["start_date"] > data["end_date"]:
            raise ValidationError(
                "start_date must be before or equal to end_date"
            )
        
class LeaveDeleteSchema(Schema):
    leave_id = fields.UUID(required=True)
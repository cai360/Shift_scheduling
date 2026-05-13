from marshmallow import (Schema, fields, validate, validates_schema, ValidationError)
from sqlalchemy.dialects.postgresql import UUID

class LeaveCreateSchema(Schema):

    # start_date = fields.Date(required=True) #yyyy-mm-dd
    # end_date = fields.Date(required=True)

    # start_time = fields.Time(required=True) ##hh:mm
    # end_time = fields.Time(required=True)

    start_at = fields.DateTime(required=True)
    end_at = fields.DateTime(required=True)

    type = fields.String(required=True)
    
    reason = fields.String(required=True)

    reviewed_by = fields.UUID(required=True)

    @validates_schema
    def validate_date_range(self, data, **kwargs):
        if data["start_at"] > data["end_at"]:
            raise ValidationError(
                "start_at must be before or equal to end_at"
            )

        
class LeaveOutSchema(Schema):
    id = fields.UUID(dump_only=True)
    user_id = fields.UUID(dump_only=True)
    company_id = fields.UUID(dump_only=True)

    start_at = fields.DateTime(dump_only=True)
    end_at = fields.DateTime(dump_only=True)

    status = fields.String(dump_only=True)
    type = fields.String(dump_only=True, required=True, validate=validate.OneOf(["sick", "annual", "personal"]))
    reason = fields.String(dump_only=True)

    reject_reason = fields.String(dump_only=True, allow_none=True)

    reviewed_at = fields.DateTime(dump_only=True, allow_none=True)
    reviewed_by = fields.UUID(dump_only=True, allow_none=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True, allow_none=True)


class LeaveReviewSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf(["pending","approved", "rejected", "withdrawn"]))
    reject_reason = fields.String(allow_none=True)

class LeaveWithdrawnSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf(["withdrawn"]))

class LeaveUpdateSchema(Schema):
    start_at = fields.DateTime(required=True)
    end_at = fields.DateTime(required=True)

    type = fields.String(required=True)
    reason = fields.String(required=True)

    reviewed_by = fields.UUID(required=True)

    @validates_schema
    def validate_date_range(self, data, **kwargs):
        if data["start_at"] > data["end_at"]:
            raise ValidationError(
                "start_at must be before or equal to end_at"
            )

class LeaveListSchema(Schema):
    scope = fields.Str(
        load_default="self",
        validate=validate.OneOf(["self", "all"])
    )

class LeaveDeleteSchema(Schema):
    leave_id = fields.UUID(required=True)
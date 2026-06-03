from marshmallow import (Schema, fields, validate, validates_schema, ValidationError)
from sqlalchemy.dialects.postgresql import UUID

class LeaveCreateSchema(Schema):
    start_at = fields.DateTime(required=True)
    end_at = fields.DateTime(required=True)

    leave_type = fields.String(required=True, validate=validate.OneOf(["sick", "annual", "personal"]))
    
    reason = fields.String(required=True)

    assigned_reviewer_id = fields.UUID(required=False)

    @validates_schema
    def validate_date_range(self, data, **kwargs):
        if data["start_at"] >= data["end_at"]:
            raise ValidationError(
                "start_at must be earlier than end_at"
            )

        
class LeaveOutSchema(Schema):
    id = fields.UUID(dump_only=True)
    user_id = fields.UUID(dump_only=True)
    company_id = fields.UUID(dump_only=True)

    start_at = fields.DateTime(dump_only=True)
    end_at = fields.DateTime(dump_only=True)

    status = fields.String(dump_only=True)
    leave_type = fields.String(dump_only=True, validate=validate.OneOf(["sick", "annual", "personal"]))
    reason = fields.String(dump_only=True)

    reject_reason = fields.String(dump_only=True, allow_none=True)

    reviewed_at = fields.DateTime(dump_only=True, allow_none=True)
    reviewed_by = fields.UUID(dump_only=True, allow_none=True)
    assigned_reviewer_id = fields.UUID(dump_only=True, allow_none=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True, allow_none=True)

class LeaveReviewSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf(["approved", "rejected"]))
    reject_reason = fields.String(allow_none=True)

class LeaveUpdateSchema(Schema):
    start_at = fields.DateTime(required=True)
    end_at = fields.DateTime(required=True)
    leave_type = fields.String(required=True, validate=validate.OneOf(["sick", "annual", "personal"]))
    reason = fields.String(required=True)

    assigned_reviewer_id = fields.UUID(required=True)

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
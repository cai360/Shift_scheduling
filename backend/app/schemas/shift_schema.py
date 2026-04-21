from marshmallow import (Schema, fields, validate, validates_schema, ValidationError)
from sqlalchemy.dialects.postgresql import UUID
from app.schemas.assignment_schema import AssignmentOutSchema

class ShiftCreateRequestSchema(Schema):
    """
    NOTE:
    MVP supports a single continuous working period per day.
    Support for multiple working periods (e.g. lunch breaks)
    will be added via a different request schema in the future.
    """
    start_date = fields.Date(required=True) #yyyy-mm-dd
    end_date = fields.Date(required=True)

    start_time = fields.Time(required=True) ##hh:mm
    end_time = fields.Time(required=True)

    interval_minutes = fields.Integer(
        required=True,
        validate=validate.Range(min=30)
    )

    capacity = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

    @validates_schema
    def validate_date_range(self, data, **kwargs):
        if data["start_date"] > data["end_date"]:
            raise ValidationError(
                "start_date must be before or equal to end_date"
            )

        
class ShiftOutSchema(Schema):
    id = fields.UUID(dump_only=True)
    company_id = fields.UUID(dump_only=True)

    start_at = fields.DateTime(dump_only=True)
    end_at = fields.DateTime(dump_only=True)

    capacity = fields.Integer(dump_only=True)

    published_at = fields.DateTime(dump_only=True, allow_none=True)
    deleted_at = fields.DateTime(dump_only=True, allow_none=True)

    # assignments = fields.Nested(AssignmentOutSchema, many=True)
    # temporarily removed for list API to reduce payload size

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    status = fields.Method("get_status")
    assignment_count = fields.Method("get_assigned_count")
    remaining_capacity = fields.Method("get_remaining_capacity")

    def get_status(self, obj):
        return "published" if obj.published_at else "draft"
    
    def get_assigned_count(self, obj):
        return len(obj.assignments or [])
    
    def get_remaining_capacity(self, obj):
        return obj.capacity - len(obj.assignments or [])


class ShiftPublishSchema(Schema):
    shift_ids = fields.List(
        fields.UUID(),
        required = True,
        validate = validate.Length(min=1)
    )

class ShiftUpdateSchema(Schema):
    start_time = fields.DateTime(required=False)
    end_time = fields.DateTime(required=False)

    capacity = fields.Integer(
        required=False,
        validate=validate.Range(min=1)
    )

    @validates_schema
    def validate_time_range(self, data, **kwargs):
        start = data.get("start_time") #hh:mm
        end = data.get("end_time")#hh:mm

        if start and end and start == end:
            raise ValidationError(
                "start_time and end_time cannot be the same."
            )

class ShiftBulkDeleteSchema(Schema):
    shift_ids = fields.List(
        fields.UUID(),
        required=True,
        validate=validate.Length(min=1)
    )

class ShiftQuerySchema(Schema):
    status = fields.Str(required=False)
    from_ = fields.Str(data_key="from", required=False)
    to_ = fields.Str(data_key="to", required=False)



# class WorkingPeriodSchema(Schema):
#     start_time = fields.Time(required=True)
#     end_time = fields.Time(required=True)

from marshmallow import (
    Schema,
    fields,
    validate,
    validates_schema,
    ValidationError,
)

class ShiftCreateRequestSchema(Schema):
    """
    NOTE:
    MVP supports a single continuous working period per day.
    Support for multiple working periods (e.g. lunch breaks)
    will be added via a different request schema in the future.
    """
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

    start_time = fields.Time(required=True)
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

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class ShiftUpdateSchema(Schema):
    capacity = fields.Integer(
        required=False,
        validate=validate.Range(min=1)
    )



# class WorkingPeriodSchema(Schema):
#     start_time = fields.Time(required=True)
#     end_time = fields.Time(required=True)

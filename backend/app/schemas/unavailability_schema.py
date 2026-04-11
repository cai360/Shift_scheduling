from marshmallow import Schema, fields, validates_schema, ValidationError, validate


class UnavailabilityCreateSchema(Schema):
    start_at = fields.DateTime(required=True)
    end_at = fields.DateTime(required=True)

    @validates_schema
    def validate_date_range(self, data, **kwargs):
        start_at = data["start_at"]
        end_at = data["end_at"]

        validate_timezone_aware(start_at, "start_at")
        validate_timezone_aware(end_at, "end_at")

        if start_at > end_at:
            raise ValidationError("end_at must be after start_at.")

class UnavailabilityUpdateSchema(Schema):
    start_at = fields.DateTime(required=True)
    end_at = fields.DateTime(required=True)
    
    @validates_schema
    def validate_date_range(self, data, **kwargs):
        start_at = data["start_at"]
        end_at = data["end_at"]

        validate_timezone_aware(start_at, "start_at")
        validate_timezone_aware(end_at, "end_at")

        if start_at > end_at:
            raise ValidationError("end_at must be after start_at.")

class UnavailabilityOutSchema(Schema):
    id = fields.UUID()
    user_id = fields.UUID(required=True)
    company_id = fields.UUID(required=True)
    start_at = fields.DateTime(required=True)
    end_at = fields.DateTime(required=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
    deleted_at = fields.DateTime(required=None)

def validate_timezone_aware(dt, field_name):
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise ValidationError(
            f"{field_name} must be timezone-aware (include timezone info)."
        )
    
class UnavailabilityListSchema(Schema):
    scope = fields.Str(
        load_default="self",
        validate=validate.OneOf(["self", "all"])
    )

from marshmallow import Schema, fields, ValidationError, validates

class AssignmentCreateSchema(Schema):
    user_id = fields.UUID(required=True)
    shift_ids = fields.List(fields.UUID(), required=True)

    @validates("shift_ids")
    def validate_unique_shift_ids(self, value, **kwargs):
        if len(value) != len(set(value)):
            raise ValidationError("shift_ids must be unique")
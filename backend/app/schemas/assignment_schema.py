from marshmallow import Schema, fields, ValidationError, validates

class AssignmentCreateSchema(Schema):
    user_id = fields.UUID(required=True)
    shift_ids = fields.List(fields.UUID(), required=True)

    @validates("shift_ids")
    def validate_unique_shift_ids(self, value, **kwargs):
        if len(value) != len(set(value)):
            raise ValidationError("shift_ids must be unique")
        
class AssignmentOutSchema(Schema):
    id = fields.UUID(required=True)
    user_id = fields.UUID()
    assigned_by = fields.UUID()
        
class AssignmentBatchDeleteSchema(Schema):
    assignment_ids = fields.List(
        fields.UUID(),
        required=True,
    )

    @validates("assignment_ids")
    def validate_unique_assignment_ids(self, value, **kwargs):
        if not value:
            raise ValidationError("assignment_ids must not be empty")

        if len(value) != len(set(value)):
            raise ValidationError("assignment_ids must be unique")
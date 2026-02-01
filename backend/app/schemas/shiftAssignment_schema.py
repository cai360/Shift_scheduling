from marshmallow import Schema, fields, validate

class AssignmentCreateSchema(Schema):
    user_id = fields.UUID(required=True)
    shift_ids = fields.List(
        fields.UUID(),
        required = True,
        validate=[
            validate.Length(min=1),
            validate.Unique()
        ]
    )
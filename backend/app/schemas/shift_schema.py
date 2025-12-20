from marshmallow import Schema, fields, validate

class ShiftCreateRequestSchema(Schema):
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    start_time = fields.Time(required=True)
    end_time = fields.Time(required=True)
    interval_minutes = fields.Integer(
        required=True,
        validate=validate.Range(min=30) #最小間隔預設 30min
    )
    capacity = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )

class ShiftOutSchema(Schema):
    id = fields.UUID(dump_only=True)
    company_id = fields.UUID(dump_only=True)
    date = fields.Date()
    start_time = fields.Time()
    end_time = fields.Time()
    capacity = fields.Time()
    publiched_at = fields.DateTime(allow_none=True)
    delete_at = fields.DateTime(allow_none=True)
    created_at = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime(allow_none=True)

class ShiftUpdateSchema(Schema):
    starting_time = fields.Time(required=False)
    ending_time = fields.Time(required=False)
    capacity = fields.Integer(
        required=False,
        validate=validate.Range(min=1)
    )

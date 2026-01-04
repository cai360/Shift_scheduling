from flask import Blueprint, jsonify, request
from app.schemas.shift_schema import ShiftCreateRequestSchema, ShiftOutSchema
from app.utils.auth_decorators import jwt_required
from app.services.shift_service import ShiftService
from app.utils.response import ok, error

bp = Blueprint("shifts", __name__)


@bp.get("/ping")
def ping():
    return jsonify({"message": "pong shifts"})

@bp.post("/<company_id>/shifts/bulk")
@jwt_required
def create_empty_shifts(company_id):
    payload = request.get_json() or {}
    data = ShiftCreateRequestSchema().load(payload)

    shifts = ShiftService.create_shifts_bulk(
        data = data,
        user_id = g.user_id,
        company_id = company_id
    )

    return ok(ShiftOutSchema(many=True).dump(shifts), 201)

@bp.get("/companies/<company_id>/shifts")
def get_shift():
    ...
from flask import Blueprint, jsonify, request, g
from app.schemas.shift_schema import *
from app.utils.auth_decorators import jwt_required
from app.services.shift_service import ShiftService
from app.utils.response import ok, error

bp = Blueprint("shifts", __name__)


@bp.get("/ping")
def ping():
    return jsonify({"message": "ping shifts"})

@bp.post("companies/<company_id>/shifts/bulk")
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
@jwt_required
def get_shifts(company_id):
    shfits = ShiftService.list_shifts_by_company(
        company_id=company_id,
        user_id=g.user_id
        )
    
    return ok(ShiftOutSchema(many=True).dump(shfits))


@bp.post("/companies/<company_id>/shifts/publish")
@jwt_required
def publish_shifts(company_id):
    payload = request.get_json(silent=True) or {}

    data = ShiftPublishSchema().load(payload)

    result = ShiftService.publish_shifts(
        company_id=company_id,
        user_id=g.user_id,
        shift_ids=data["shift_ids"]
    )

    return ok(result, 200)

@bp.delete("/shifts/<shift_id>")
@jwt_required
def delect_draft_shift(shift_id):
    ShiftService.delete_shift(
        shift_id=shift_id,
        user_id=g.user_id
    )
    return "", 204

from flask import Blueprint, jsonify, request, g
from app.schemas.leave_schema import *
from app.utils.auth_decorators import jwt_required
from app.utils.datetime_utils import parse_datetime
from app.services.shift_service import ShiftService
from app.utils.response import ok, error
from dateutil.parser import isoparse
from app.config import BUSINESS_TZ


bp = Blueprint("leaves", __name__)


@bp.post("companies/<company_id>/leave")
@jwt_required
def create_leave(company_id):
    payload = request.get_json() or {}
    data = LeaveCreateSchema().load(payload)

    leave = ShiftService.create_shifts_bulk(
        data = data,
        user_id = g.user_id,
        company_id = company_id
    )

    return ok(ShiftOutSchema(many=True).dump(shifts), 201)

@bp.get("/companies/<company_id>/leaves")
@jwt_required
def get_shifts(company_id):
    """
    Query params:
    - status: optional[str] = "published"
    - from:   optional[ISO-8601 datetime]
    - to:     optional[ISO-8601 datetime]
    """
    query = ShiftQuerySchema().load(request.args)
    try:
        from_ = parse_datetime(query["from_"]) if "from_" in query else None
        to_ = parse_datetime(query["to_"]) if "to_" in query else None
    except ValueError:
        raise ValueError("Invalid datetime format.")

    shifts = ShiftService.list_shifts_by_company(
        company_id=company_id,
        user_id=g.user_id,
        status=query.get("status"),
        from_=from_,
        to_=to_
        )
    
    return ok(ShiftOutSchema(many=True).dump(shifts))


@bp.post("/companies/<company_id>/shifts/publish")
@jwt_required
def list_leaves(company_id):
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
def delect_shift(shift_id):
    ShiftService.delete_shift(
        shift_id=shift_id,
        user_id=g.user_id
    )
    return "", 204

@bp.patch("shifts/<shift_id>")
@jwt_required
def update_shift(shift_id):
    data = ShiftUpdateSchema().load(request.json or {})
    shift = ShiftService.update_shift(
        shift_id=shift_id,
        user_id=g.user_id,
        data=data
    )
    return ok(ShiftOutSchema().dump(shift))

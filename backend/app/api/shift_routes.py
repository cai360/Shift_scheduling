from flask import Blueprint, request, g
from app.schemas.shift_schema import *
from app.utils.auth_decorators import jwt_required
from app.services.shift_service import ShiftService
from app.utils.response import ok


bp = Blueprint("shifts", __name__, url_prefix="/companies/<uuid:company_id>/shifts")


@bp.post("/bulk")
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

@bp.get("")
@jwt_required
def get_shifts(company_id):
    """
    Query params:
<<<<<<< HEAD
    - status: optional[str] = "published"
    - from:   optional[date] inclusive start (YYYY-MM-DD)
    - to:     optional[date] exclusive end (YYYY-MM-DD)
=======
    - status: optional[str]
    - from:   optional[YYYY-MM-DD]
    - to:     optional[YYYY-MM-DD]
>>>>>>> ccc00e7 (refactor(shift): update lifecycle to allow assign on draft/published)
    """
    query = ShiftQuerySchema().load(request.args)

    shifts = ShiftService.list_shifts_by_company(
        company_id=company_id,
        user_id=g.user_id,
<<<<<<< HEAD
        status=query.get("status"),
        from_=query.get("from_"),
        to_=query.get("to_"),
    )
    
=======
        status=query.get("status") or None,
        from_=query.get("from_"),
        to_=query.get("to_"),
    )

>>>>>>> ccc00e7 (refactor(shift): update lifecycle to allow assign on draft/published)
    return ok(ShiftOutSchema(many=True).dump(shifts))


@bp.post("/publish")
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

@bp.delete("/<uuid:shift_id>")
@jwt_required
def delete_shift(company_id, shift_id):
    ShiftService.delete_shift(
        company_id=company_id,
        shift_id=shift_id,
        user_id=g.user_id
    )
    return "", 204

@bp.patch("/<uuid:shift_id>")
@jwt_required
def update_shift(company_id, shift_id):
    data = ShiftUpdateSchema().load(request.json or {})
    shift = ShiftService.update_shift(
        company_id=company_id,
        shift_id=shift_id,
        user_id=g.user_id,
        data=data
    )
    return ok(ShiftOutSchema().dump(shift))

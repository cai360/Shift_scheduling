from flask import Blueprint, request, g
from app.schemas.shift_schema import *
from app.schemas.shiftAssignment_schema import *
from app.utils.auth_decorators import jwt_required
from app.utils.response import ok, error
from app.services.assignment_service import *

bp = Blueprint("assignment", __name__)

@bp.post("/companies/<uuid:company_id>/assignments")
@jwt_required
def assignment_shifts_to_user(company_id):
    data = AssignmentCreateSchema().load(request.json or {})
    AssignmentService.assign_user_to_shifts(
        company_id = company_id,
        actor_user_id = g.user_id,
        target_user_id = data["user_id"],
        shift_ids = data["shift_ids"]
    )

    return ok({}, 204)
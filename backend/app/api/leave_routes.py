from flask import Blueprint, jsonify, request, g
from app.schemas.leave_schema import *
from app.utils.auth_decorators import jwt_required
from app.utils.datetime_utils import parse_datetime
from app.services.leave_service import LeaveService
from app.utils.response import ok, error
from dateutil.parser import isoparse
from app.config import BUSINESS_TZ


bp = Blueprint("leaves", __name__)


@bp.post("/companies/<company_id>/leaves")
@jwt_required
def create_leave(company_id):
    data = LeaveCreateSchema().load(request.get_json() or {})
    leave = LeaveService.create_leave(
        data = data,
        user_id = g.user_id,
        company_id = company_id
    )

    return ok(LeaveOutSchema().dump(leave), 201)

@bp.get("/companies/<company_id>/leaves/<uuid:leave_id>")
@jwt_required
def get_leave(company_id, leave_id):
    leave = LeaveService.get_leave(
        leave_id=leave_id,
        company_id=company_id,
        user_id=g.user_id,
        )
    
    return ok(LeaveOutSchema().dump(leave))


@bp.get("/companies/<company_id>/leaves")
@jwt_required
def list_leaves(company_id):

    data = LeaveListSchema().load(request.args)

    result = LeaveService.list_leaves(
        user_id=g.user_id,
        company_id=company_id,
        scope=data["scope"]
    )

    return ok(LeaveOutSchema(many=True).dump(result), 200)

@bp.delete("/companies/<company_id>/leaves/<uuid:leave_id>")
@jwt_required
def delete_leave(company_id, leave_id):
    LeaveService.delete_leave(
        leave_id=leave_id,
        user_id=g.user_id,
        company_id=company_id
    )
    return "", 204

@bp.patch("/companies/<company_id>/leaves/<uuid:leave_id>")
@jwt_required
def update_leave(leave_id, company_id):
    data = LeaveUpdateSchema().load(request.json or {})
    leave = LeaveService.update_leave(
        leave_id=leave_id,
        user_id=g.user_id,
        company_id=company_id,
        data=data
    )
    return ok(LeaveOutSchema().dump(leave))

@bp.post("/companies/<company_id>/leaves/<uuid:leave_id>")
@jwt_required
def review_leave(leave_id, company_id):
    data = LeaveReviewSchema().load(request.json or {})
    leave = LeaveService.review_leave(
        leave_id=leave_id,
        user_id=g.user_id,
        company_id=company_id,
        data=data
    )
    return ok(LeaveOutSchema().dump(leave))

# @bp.post("/companies/<company_id>/leaves/<uuid:leave_id>")
# @jwt_required
# def withdrawn_leave(leave_id, company_id):
#     data = LeaveWithdrawnSchema().load(request.json or {})
#     leave = LeaveService.withdrawn_leave(
#         leave_id=leave_id,
#         user_id=g.user_id,
#         company_id=company_id,
#         data=data
#     )
#     return ok(LeaveOutSchema().dump(leave))

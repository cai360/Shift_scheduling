from flask import Blueprint, request, g
from app.extensions import db
from app.models.unavailability import Unavailability
from app.schemas.unavailability_schema import *
from app.utils.auth_decorators import jwt_required
from app.utils.response import ok, error
from app.services.unavailability_service import UnavailabilityService

bp = Blueprint("unavailabilities", __name__, url_prefix="/companies/<uuid:company_id>/unavailabilities")

@bp.post("")
@jwt_required
def create_unavailability(company_id):
    data = UnavailabilityCreateSchema().load(request.json or {})

    unavailability = UnavailabilityService.create_unavailability(
        data, 
        g.user_id,
        company_id=company_id
        )
    return ok(UnavailabilityOutSchema().dump(unavailability), 201)


@bp.get("/<uuid:unavailability_id>")
@jwt_required
def get_unavailability(company_id, unavailability_id):
    unavailability = UnavailabilityService.get_unavailability(
        unavailability_id,
        user_id=g.user_id,
        company_id=company_id
    )
    return ok(UnavailabilityOutSchema().dump(unavailability))

# List unavailabilities for the current user
@bp.get("")
@jwt_required
def list_for_user(company_id):
    unavailability = UnavailabilityService.list_unavailabilities(
        user_id=g.user_id, 
        company_id=company_id
    )
    return ok(UnavailabilityOutSchema(many=True).dump(unavailability))

@bp.patch("/<uuid:unavailability_id>")
@jwt_required
def update_unavailability(company_id, unavailability_id):
    data = UnavailabilityUpdateSchema().load(request.json or {})
    unavailability = UnavailabilityService.update_unavailability(unavailability_id, g.user_id, company_id, data)
    return ok(UnavailabilityOutSchema().dump(unavailability))

@bp.delete("/<uuid:unavailability_id>")
@jwt_required
def delete_unavailability(company_id, unavailability_id):
    UnavailabilityService.delete_unavailability(unavailability_id, g.user_id, company_id)
    return "", 204


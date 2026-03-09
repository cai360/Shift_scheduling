from flask import Blueprint, request,g
from app.extensions import db
from app.models.companies import Company
from app.schemas.company_schema import * 
from app.schemas.companyUser_schema import CompanyUserOutSchema, TransferOwnershipSchema
from app.utils.auth_decorators import jwt_required
from app.utils.response import ok, error
from app.services.company_service import CompanyService
from app.services.companyUser_service import CompanyUserService
from app.services.permission_services import PermissionService



bp = Blueprint("companies", __name__, url_prefix="/companies")

@bp.post("")
@jwt_required
def create_company():
    data = CompanyCreateSchema().load(request.json or {})
    company = CompanyService.create_company(data, g.user_id)
    return ok(CompanyOutSchema().dump(company), 201)


@bp.get("/<company_id>")
@jwt_required
def get_company(company_id):
    company = CompanyService.get_company(company_id)
    return ok(CompanyOutSchema().dump(company))

@bp.patch("/<company_id>")
@jwt_required
def update_company(company_id):
    data = CompanyUpdateSchema().load(request.json or {})
    company = CompanyService.update_company(company_id, data, g.user_id)
    return ok(CompanyOutSchema().dump(company))

@bp.delete("/<company_id>")
@jwt_required
def delete_company(company_id):
    PermissionService.require_owner(
        company_id=company_id,
        user_id=g.user_id
    )
    CompanyService.soft_delete_company(company_id, g.user_id)
    return "", 204


@bp.post("/<company_id>/join")
@jwt_required
def join_company(company_id):
    company_user = CompanyUserService.join_company(company_id, g.user_id)
    return ok({
        "company_id": str(company_user.company_id),
        "user_id": str(company_user.user_id),
        "role": company_user.role
    }, 201)

@bp.get("/<company_id>/users")
@jwt_required
def list_company_users(company_id):
    users =  CompanyUserService.get_members(
        company_id=company_id,
        user_id = g.user_id
    )

    return ok(CompanyUserOutSchema(many=True).dump(users))

@bp.post("/<uuid:company_id>/transfer-ownership")
@jwt_required
def transfer_ownership(company_id):
    actor_user_id = g.user_id
    data = TransferOwnershipSchema().load(request.json)

    PermissionService.require_owner(
        company_id=company_id,
        user_id=actor_user_id
    )

    result = CompanyUserService.transfer_ownership(
        company_id=company_id,
        actor_user_id=actor_user_id,
        target_user_id=data["target_user_id"]
    )

    return ok({
        "user_id": str(result.user_id),
        "company_id": str(result.company_id),
        "role": result.role
    })

@bp.post("/<uuid:company_id>/leave")
@jwt_required
def leave_company(company_id):
    CompanyUserService.leave_company(
        company_id=company_id,
        user_id = g.user_id
    )
    return ok()






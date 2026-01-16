from flask import Blueprint, request,g
from app.extensions import db
from app.models.companies import Company
from app.schemas.company_schema import * 
from app.schemas.companyUser_schema import CompanyUserOutSchema
from app.utils.auth_decorators import jwt_required
from app.utils.response import ok, error
from app.services.company_service import CompanyService
from app.services.companyUser_service import CompanyUserService



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

#TODO: add list users in a company in company_routes 

@bp.patch("/<company_id>")
@jwt_required
def update_company(company_id):
    data = CompanyUpdateSchema().load(request.json or {})
    company = CompanyService.update_company(company_id, data, g.user_id)
    return ok(CompanyOutSchema().dump(company))

@bp.delete("/<company_id>")
@jwt_required
def delete_company(company_id):
    CompanyService.soft_delete_company(company_id, g.user_id)
    return "", 204


@bp.post("/<company_id>/join")
@jwt_required
def join_company(company_id):
    company_user = CompanyService.join_company(company_id, g.user_id)
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





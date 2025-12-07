from flask import Blueprint, request,g
from app.extensions import db
from app.models.companies import Company
from app.schemas.company_schema import * 
from app.utils.auth_decorators import jwt_required
from app.utils.response import ok, error
from app.services.companny_service import CompanyService

bp = Blueprint("company", __name__, url_prefix="company")

@bp.post("/companies")
@jwt_required
@bp.post("/companies")
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

# List companies for the current user
@bp.get("/companies")
@jwt_required
def list_for_user():
    companies = CompanyService.list_companies_for_user(g.user_id)
    return ok(CompanyOutSchema(many=True).dump(companies))

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
    return ok(None, 204)


@bp.post("/<company_id>/join")
@jwt_required
def join_company(company_id):
    company_user = CompanyService.join_company(company_id, g.user_id)
    return ok({
        "company_id": str(company_user.company_id),
        "user_id": str(company_user.user_id),
        "role": company_user.role
    }, 201)


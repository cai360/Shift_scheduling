from flask import Blueprint, request, g
from app.utils.auth_decorators import jwt_required
from marshmallow import ValidationError
from app.extensions import db
from app.schemas.user_schema import *
from app.schemas.company_schema import CompanyOutSchema
from app.services.user_service import UserService
from app.utils.response import ok, error  

bp = Blueprint("users", __name__, url_prefix="/users")





@bp.patch("/me")
@jwt_required
def update_me():
    data = UserUpdateSchema().load(request.json or {})
    user = UserService.update_user(g.user_id, data)
    return ok(UserOutSchema().dump(user))


@bp.delete("/me")
@jwt_required
def delete_me():
    UserService.soft_delete_user(g.user_id)
    return "", 204


@bp.patch("/me/password")
@jwt_required
def update_password():
    payload = request.get_json(silent=True) or {}

    try:
        data = UserUpdatePasswordSchema().load(payload)
    except ValidationError as err:
        return error("Validation error", 400, err.messages)

    UserService.update_user_password(
        user_id=g.user_id,
        old_password=data["old_password"],
        new_password=data["new_password"]
    )

    return ok({"message": "Password updated successfully"}, 200)

# List companies where user belongs  for the current user
@bp.get("/me/companies")
@jwt_required
def list_user_companies():
    companies = UserService.list_companies_for_user(g.user_id)
    return ok(CompanyOutSchema(many=True).dump(companies))


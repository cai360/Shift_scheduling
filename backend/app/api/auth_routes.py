from flask import Blueprint, request
from app.schemas.auth_schema import LoginEmailSchema
from app.schemas.user_schema import UserOutSchema
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.utils.result import success_res, error_res

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    data = LoginEmailSchema().load(payload)

    user = UserService.find_user_by_email(data["email"])
    if not user:
        return error_res("Invalid email", code=401, status=401)

    pwd_field = UserService._pwd_field()
    hashed = getattr(user, pwd_field, None)
    if not hashed or not AuthService.verify_password(data["password"], hashed):
        return error_res("Invalid credentials", code=401, status=401)

    if hasattr(user, "active") and user.active is False:
        return error_res("Account disabled", code=403, status=403)

    tokens = AuthService.issue_tokens(user.id)
    resp = {"user": UserOutSchema().dump(user), **tokens}
    return success_res(resp, "Login success", status=200)


@bp.post("/refresh")
def refresh():
    payload = request.get_json(silent=True) or {}
    refresh_token = payload.get("refresh_token")

    if not refresh_token:
        return error_res("refresh_token is required", code=400, status=400)

    try:
        new_access = AuthService.issue_access_from_refresh(refresh_token)
    except ValueError as e:
        return error_res(str(e), code=401, status=401)

    return success_res(new_access, "Token refreshed", status=200)



    


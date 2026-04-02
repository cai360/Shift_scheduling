from flask import Blueprint, request,g
from app.schemas.user_schema import UserOutSchema
from app.schemas.auth_schema import *
from app.services.auth_service import AuthService
from app.utils.response import ok, error
from marshmallow import ValidationError

bp = Blueprint("auth", __name__, url_prefix="/auth")

#TODO #in the controller layer shouldn't intetactive with db
@bp.post("/register")
def register():
    payload = RegisterSchema().load(request.get_json() or {})

    user = AuthService.register_user(
        username=payload["username"],
        email=payload["email"],
        password=payload["password"],
    )

    return ok(UserOutSchema().dump(user), 201)

@bp.post("/login")
def login():
    data = LoginSchema().load(request.get_json() or {})

    tokens = AuthService.authenticate(
        data["email"],
        data["password"],
    )

    return ok(tokens, status=200)

@bp.post("/login")
@bp.post("/refresh")
def refresh():
    data = RefreshSchema().load(request.get_json() or {})

    new_access = AuthService.issue_access_from_refresh(data["refresh_token"])

    return ok(new_access, status=200)


#TODO refresh_token rotation


    


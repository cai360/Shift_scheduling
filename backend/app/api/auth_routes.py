from flask import Blueprint, request,g
from app.schemas.user_schema import UserOutSchema
from app.schemas.auth_schema import *
from app.services.auth_service import AuthService, RegisterError
from app.utils.response import ok, error
from marshmallow import ValidationError

bp = Blueprint("auth", __name__, url_prefix="/auth")

#TODO #in the controller layer shouldn't intetactive with db
@bp.post("/register")
def register():
    try:
        payload = RegisterSchema().load(request.json or {})
    except ValidationError as err:
        return error("Validation error", 400, err.messages)

    try:
        user = AuthService.register_user(
            username=payload["username"],
            email=payload["email"],
            password=payload["password"]
        )
    except RegisterError as err:
        return error(str(err), 409)

    return ok(UserOutSchema().dump(user), 201)

@bp.post("/login")
def login():
    try:
        data = LoginSchema().load(request.json or {})
    except ValidationError as err:
        return error("Validation error", status=400, details=err.messages)
    
    user = AuthService.authenticate(data["email"], data["password"])
    if not user:
        return error("Invalid email or password", status=401)

    tokens = AuthService.issue_tokens(user.id)

    return ok(tokens, status=200)

@bp.post("/refresh")
def refresh():
    try:
        data = RefreshSchema().load(request.json or {})
    except ValidationError as err:
        return error("Validation error", status=400, details=err.messages)
    
    refresh_token = data["refresh_token"]
       
    try:
        new_access = AuthService.issue_access_from_refresh(refresh_token)
    except ValueError as err:
        return error(str(err), status=401)

    return ok(new_access, status=200)


#TODO refresh_token rotation


    


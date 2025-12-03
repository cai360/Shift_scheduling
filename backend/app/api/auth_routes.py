from flask import Blueprint, request,g
from app.extensions import db
from app.models.user import User
from app.schemas.user_schema import UserCreateSchema, UserOutSchema
from app.schemas.auth_schema import LoginSchema, RefreshSchema
from app.services.auth_service import AuthService
from app.utils.response import ok, error
from marshmallow import ValidationError
from app.utils.auth_decorators import jwt_required

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.get("/me")
@jwt_required
def get_me():
    user = User.query.get(g.user_id)
    if not user:
        return error("User not found", 404)
    return ok(UserOutSchema().dump(user), 200)

@bp.post("/register")
def register():
    try:
        data = UserCreateSchema().load(request.json or {})
    except Exception as err:
        return error("Validation error", status=400, details=err.messages)

    existing = User.query.filter_by(email=data["email"]).first()
    if existing:
        return error("Email already exists", status=409)
    
    user = User(
        username = data["username"],
        email = data["email"],
        hash = AuthService.hash_password(data["password"])
    )

    db.session.add(user)
    db.session.commit()

    return ok(UserOutSchema().dump(user), status=201)

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





    


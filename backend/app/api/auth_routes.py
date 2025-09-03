from flask import Blueprint, jsonify, request
from app.schemas.auth_schema import LoginEmailSchema
from app.schemas.user_schema import UserOutSchema
from app.services.user_service import UserService
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.post("/login")
def login():
    payload = request.get_json() or {}
    data = LoginEmailSchema().load(payload)

    user = UserService.find_user_by_email(data["email"])
    if not user:
        return jsonify({"error": "Invalid email"}), 401
    
    pwd_field = UserService._pwd_field()
    hashed = getattr(user, pwd_field, None)
    if not hashed or not AuthService.verify_password(data["password"], hashed):
        return jsonify({"error": "Invalid credentials"}), 401
    
    if hasattr(user, "activce") and user.active is False:
        return jsonify({"error": "Account disabled"}), 403
    
    tokens = AuthService.issue_tokens(user.id)
    resp = {"user": UserOutSchema().dump(user), **tokens}
    return jsonify(resp), 200

def refresh():
    payload = request.get_json() or {}
    refresh_token = payload.get("refresh_token")
    if not refresh_token:
        return jsonify({"error": "refresh_token is required"}), 400
    
    try: 
        new_access = AuthService.issue_access_from_refresh(refresh_token)
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    return jsonify(new_access), 200




    


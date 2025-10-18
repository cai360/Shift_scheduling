from flask import Blueprint, request, g
from app.utils.auth_decorators import jwt_required
from marshmallow import ValidationError

from app import models
from app.extensions import db
from app.schemas.user_schema import UserCreateSchema, UserOutSchema, UserUpdateSchema
from app.services.user_service import UserService
from app.utils.result import success_res  

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.get("/me")
@jwt_required
def get_me():
    return success_res({"user_id": g.user_id}, "Get current user success")


@bp.post("")
def create_user():
    payload = request.get_json(silent=True) or {}

    data = UserCreateSchema().load(payload)
    user = UserService.create_user(data)

    return success_res(UserOutSchema().dump(user), "Create user success", status=201)


@bp.get("/<int:user_id>")
@jwt_required
def get_user(user_id: int):
    user = db.session.get(models.User, user_id)
    if not user:
        raise ValueError("User not found")

    return success_res(UserOutSchema().dump(user), "Get user success")


@bp.patch("/<int:user_id>")
@jwt_required
def update_user(user_id: int):
    payload = request.get_json(silent=True) or {}
    data = UserUpdateSchema(partial=True).load(payload)
    user = UserService.update_user(user_id, data)
    return success_res(UserOutSchema().dump(user), "Update user success")


@bp.delete("/<int:user_id>")
@jwt_required
def delete_user(user_id: int):
    user = UserService.delete_user(user_id) 
    return success_res(UserOutSchema().dump(user), "Delete user success")


@bp.get("")
@jwt_required
def get_all_users():
    users = models.User.query.order_by(models.User.id.desc()).all()
    return success_res(UserOutSchema(many=True).dump(users), "Get all users success")
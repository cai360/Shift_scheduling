from flask import Blueprint, jsonify, request
from app.utils.auth_decorators import jwt_required
from marshmallow import ValidationError

from app import models
from app.extensions import db
from app.schemas.user_schema import UserCreateSchema, UserOutSchema, UserUpdateSchema
from app.services.user_service import UserService
#from app.api.auth_decorators import jwt_required

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.get("/ping")
def ping():
    return jsonify({"message": "ping"})

@bp.post("")
def create_user():
    payload = request.get_json(silent=True) or {}
    try:
        data = UserCreateSchema().load(payload)
    except ValidationError as ve:
        return jsonify({"error": ve.messages}), 400

    try:
        user = UserService.create_user(data)
        return jsonify(UserOutSchema().dump(user)), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.get("/<int:user_id>")
@jwt_required
def get_user(user_id: int):
    user = db.session.get(models.User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(UserOutSchema().dump(user)), 200

@bp.patch("/<int:user_id>")
@jwt_required
def update_user(user_id: int):
    payload = request.get_json(silent=True) or {}

    try:
        data = UserUpdateSchema(partial=True).load(payload)
    except ValidationError as ve:
        return jsonify({"error": ve.messages}), 400


    try:
        user = UserService.update_user(user_id, data) 
        return jsonify(UserOutSchema().dump(user)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.delete("/<int:user_id>")
@jwt_required
def delete_user(user_id: int):
    user = UserService.delete_user(user_id)
    return jsonify(UserOutSchema().dump(user)), 200

@bp.get("")
@jwt_required
def get_all_users():
    users = models.User.query.order_by(models.User.id.desc()).all()
    return jsonify({"data": UserOutSchema(many=True).dump(users)}), 200

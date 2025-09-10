from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from app import models
from app.schemas.user_schema import UserCreateSchema, UserOutSchema, UserUpdateSchema
from app.services.user_service import UserService

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
def get_user(user_id: int):
    user = models.User.query.get_or_404(user_id)
    return jsonify(UserOutSchema().dump(user)), 200

@bp.patch("/<int:user_id>")
def update_user(user_id: int):
    payload = request.get_json(silent=True) or {}

    # 1) validate input for PATCH (partial update)
    try:
        data = UserUpdateSchema(partial=True).load(payload)
    except ValidationError as ve:
        return jsonify({"error": ve.messages}), 400

    # 2) perform update
    try:
        user = UserService.update_user(user_id, data)  # (id, data)
        return jsonify(UserOutSchema().dump(user)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.delete("/<int:user_id>")
def delete_user(user_id: int):
    user = UserService.delete_user(user_id)
    return jsonify(UserOutSchema().dump(user)), 200

@bp.get("")
def get_all_users():
    users = models.User.query.order_by(models.User.id.desc()).all()
    return jsonify({"data": UserOutSchema(many=True).dump(users)}), 200

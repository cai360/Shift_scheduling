from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app import models
from app.schemas.user_schema import UserCreateSchema, UserOutSchema, UserUpdateSchema
from app.services.user_service import UserService

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.get('/ping')
def ping():
    return jsonify({'message': 'ping'})

@bp.post("")
def create_user():
    payload = request.get_json() or {}
    data = UserCreateSchema().load(payload)
    try:
       user = UserService.create_user(data)
       return jsonify(UserOutSchema().dump(user)), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.get("/<user_id>")
def get_user(user_id: int):
    user = models.User.query.get_or_404(user_id)
    return jsonify(UserOutSchema().dump(user))

@bp.patch("/<user_id>")
def update_user(user_id: int):
    payload = request.get_json() or {}
    data = UserUpdateSchema().load(payload)

    try:
        user = UserService.update_user(user_id, data)
    except ValueError as e:
        return jsonify({"error": str(e)}, 400)
    return jsonify(UserOutSchema().dump(user)), 200

@bp.delete("/<user_id>")
def delete_user(user_id):
    user = UserService.delete_user(user_id)
    return jsonify(UserOutSchema().dump(user)), 200


@bp.get("")
def get_all_users():
    usres = models.User.query.order_by(models.User.id.desc()).all()
    return jsonify({"data": UserOutSchema(many=True).dump(usres)}), 200






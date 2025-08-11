from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app import models
from app.schemas.user import UserCreateSchema, UserOutSchema

user_bp = Blueprint("users", __name__, url_prefix="/api/users")


@user_bp.route('/ping')
def ping():
    return jsonify({'message': 'ping'})

@user_bp.post("")
def create_user():
    payload = request.get_json() or {}
    data = UserCreateSchema().load(payload)

    u = models.User(**data)
    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        #「全部還原，不要這次的資料庫變更」
        db.session.rollback()
        return jsonify({"error": "User already exists"}), 400
    
    return jsonify(UserOutSchema().dump(u)), 201





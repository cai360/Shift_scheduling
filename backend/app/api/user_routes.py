from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app import models
from app.schemas.user_schema import UserCreateSchema, UserOutSchema, UserUpdateSchema

user_bp = Blueprint("users", __name__, url_prefix="/users")


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
        db.session.rollback()
        return jsonify({"error": "message"}), 400
    
    return jsonify(UserOutSchema().dump(u)), 201

@user_bp.get("/<user_id>")
def get_user(user_id):
    user = models.User.query.get_or_404(user_id)
    return jsonify(UserOutSchema().dump(user))

@user_bp.patch("/<user_id>")
def update_user(user_id):
    user = models.User.query.get_or_404(user_id)
    payload = request.get_json() or {}
    data = UserUpdateSchema().load(payload)

    for key, value in data.items(): 
        setattr(user, key, value)
    db.session.commit()
    return jsonify(UserOutSchema().dump(user))



@user_bp.get("")
def get_all_users():
    usres = models.User.query.order_by(models.User.id.desc()).all()
    return jsonify({"data": UserOutSchema(many=True).dump(usres)}), 200






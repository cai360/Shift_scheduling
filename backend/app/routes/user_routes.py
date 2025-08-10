from flask import Blueprint, jsonify
from app.extensions import db


user_bp = Blueprint('user', __name__)

@user_bp.route('/ping')
def ping():
    return jsonify({'message': 'pong'})
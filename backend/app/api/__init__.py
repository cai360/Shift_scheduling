from flask import Blueprint
from .user_routes import bp as users_bp
from .shift_routes import bp as shifts_bp
from .auth_routes import bp as auth_bp

api_bp = Blueprint("api", __name__, url_prefix="/api")  # add url_prefix

api_bp.register_blueprint(auth_bp)       
api_bp.register_blueprint(users_bp)
api_bp.register_blueprint(shifts_bp)

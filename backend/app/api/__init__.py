from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

from .user_routes import bp as users_bp
from .shift_routes import bp as shifts_bp

api_bp.register_blueprint(users_bp)
api_bp.register_blueprint(shifts_bp)
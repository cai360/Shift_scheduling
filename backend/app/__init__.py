from dotenv import load_dotenv
import os
#load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from flask import Flask
from flask_cors import CORS
from .extensions import db, migrate
from .api import api_bp
from .config import Config
from app.utils.error_handlers import register_error_handlers
import logging

logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
)

def create_app(config_object=None):
    app = Flask(__name__)

    allowed_origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")]
    CORS(app, supports_credentials=True, origins=allowed_origins)

    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object(Config)

    is_production = os.environ.get("FLASK_ENV") == "production"
    app.config.update(
        SESSION_COOKIE_SAMESITE="None",
        SESSION_COOKIE_SECURE=is_production,
    )

    # Bind SQLAlchemy to this Flask app
    db.init_app(app)

    # Initialize Alembic (Flask-Migrate)
    migrate.init_app(app, db)

    # Ensure models are imported so migrations can detect them
    from . import models

    # Register only the parent API blueprint
    app.register_blueprint(api_bp)

    register_error_handlers(app)
    return app


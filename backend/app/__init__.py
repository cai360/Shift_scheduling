from flask import Flask
from .config import Config
from .extensions import db, migrate
from flask_cors import CORS
from .api import api_bp



def create_app(config_object=None):
    app = Flask(__name__)
    CORS(app) 

    if config_object:
        app.config.from_object(config_object)
    else: 
        app.config.from_object(Config)

    # Bind SQLAlchemy to this Flask app
    db.init_app(app)

    # Initialize Alembic (Flask-Migrate)
    migrate.init_app(app, db)

    # Ensure models are imported so migrations can detect them
    from . import models

    # Register only the parent API blueprint
    app.register_blueprint(api_bp)
    return app


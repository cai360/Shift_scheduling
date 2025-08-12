from flask import Flask
from .config import Config
from .extensions import db, migrate
from .models import db 
from flask_cors import CORS 
from .api import api_bp



def create_app(config_object=None):
    app = Flask(__name__)
    CORS(app) 

    if config_object:
        app.config.from_object(config_object)
    else: 
        app.config.from_object(Config)

    db.init_app(app) 
    migrate.init_app(app, db)  

    from .api.user_routes import user_bp
    app.register_blueprint(api_bp)


    return app



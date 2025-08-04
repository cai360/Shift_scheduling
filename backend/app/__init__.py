from flask import Flask
from .config import Config
from flask_migrate import Migrate
from .models import db  

migrate = Migrate()  

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)  

    from .services.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/users')

    return app



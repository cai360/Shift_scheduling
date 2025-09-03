from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# To create an empty SQLAlchemy instance
db = SQLAlchemy()

# To create an empty Migrate instance
migrate = Migrate()  
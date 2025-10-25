import os
from dotenv import load_dotenv

load_dotenv()  
class TestConfig:
    TESTING = True
    # Use the same database as production but with transaction rollback for isolation
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
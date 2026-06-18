import os
from dotenv import load_dotenv

load_dotenv()  
class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.getenv("JWT_SECRET", "test-jwt-secret")
    JWT_ACCESS_EXPIRES_MINUTES = 15
    JWT_REFRESH_EXPIRES_DAYS = 7
    WTF_CSRF_ENABLED = False

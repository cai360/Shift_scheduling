import os
from dotenv import load_dotenv

load_dotenv()  
class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
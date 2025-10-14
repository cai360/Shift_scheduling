import pytest
from app import create_app
from app.extensions import db
from app.config_test import TestConfig
from flask_migrate import upgrade

@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        # Run migrations to create tables
        upgrade()
        yield app
        # Clean up after each test
        db.session.remove()

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def auth_client(client):
    from app.models import User
    from app.extensions import db
    from app.services.auth_service import AuthService

    # Create a fresh test user for each test
    user = User(email="test@example.com", username="testuser", hash=AuthService.hash_password("password001"))
    db.session.add(user)
    db.session.commit()

    tokens = AuthService.issue_tokens(user.id)
    access_token = tokens["access_token"]

    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
    return client

@pytest.fixture(autouse=True)
def clean_db(app):
    """Automatically clean the database after each test"""
    yield
    with app.app_context():
        # Rollback any uncommitted transactions
        db.session.rollback()
        # Clear all tables
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
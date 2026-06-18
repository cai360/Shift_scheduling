import pytest
from app import create_app
from app.extensions import db
from app.config_test import TestConfig

@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def api_client(client):
    class ApiClient:
        def __init__(self, flask_client):
            self.client = flask_client

        def get(self, path, token=None, **kwargs):
            return self.client.get(path, headers=self._headers(token), **kwargs)

        def post(self, path, json=None, token=None, **kwargs):
            return self.client.post(path, json=json, headers=self._headers(token), **kwargs)

        def patch(self, path, json=None, token=None, **kwargs):
            return self.client.patch(path, json=json, headers=self._headers(token), **kwargs)

        def delete(self, path, token=None, **kwargs):
            return self.client.delete(path, headers=self._headers(token), **kwargs)

        @staticmethod
        def json(response):
            return response.get_json()

        @staticmethod
        def data(response):
            return response.get_json()["data"]

        @staticmethod
        def _headers(token):
            return {"Authorization": f"Bearer {token}"} if token else {}

    return ApiClient(client)

@pytest.fixture()
def user_factory(app):
    from app.models import User
    from app.services.auth_service import AuthService

    def create_user(email="test@example.com", username="testuser", password="password001"):
        user = User(
            email=email,
            username=username,
            hash=AuthService.hash_password(password)
        )
        db.session.add(user)
        db.session.commit()
        return user

    return create_user

@pytest.fixture()
def login_as(client, user_factory):
    def login(email="test@example.com", username="testuser", password="password001"):
        user = user_factory(email=email, username=username, password=password)
        response = client.post("/api/auth/login", json={
            "email": email,
            "password": password,
        })
        tokens = response.get_json()["data"]
        return user, tokens

    return login

@pytest.fixture()
def auth_client(client, user_factory):
    from app.services.auth_service import AuthService

    user = user_factory()

    tokens = AuthService.issue_tokens(user.id)
    access_token = tokens["access_token"]

    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
    return client

@pytest.fixture(autouse=True)
def clean_db(app):
    yield
    with app.app_context():
        db.session.rollback()
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

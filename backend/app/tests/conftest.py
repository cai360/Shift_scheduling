import pytest
from app import create_app
from app.extensions import db
from app.config_test import TestConfig
from flask_migrate import upgrade

@pytest.fixture()
def test_app():
    app = create_app(TestConfig)

    with app.app_context():
        upgrade()
        yield app

        db.session.remove()
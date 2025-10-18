
def test_me_required_auth(client):
    resp = client.get("/api/users/me")
    assert resp.status_code == 401

def test_me_with_valid_token(client):
    from app.models import User
    from app.extensions import db
    from app.services.auth_service import AuthService

    user = User.query.filter_by(email="test@example.com").first()
    if not user:
        user = User(
            email="test@example.com",
            username="testuser",
            hash=AuthService.hash_password("password001")
        )
        db.session.add(user)
        db.session.commit()

    login_resp = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password001",
    })

    assert login_resp.status_code == 200

    login_data = login_resp.get_json()["data"]
    token = login_data["access_token"]

    resp = client.get("/api/users/me", headers={
        "Authorization": f"Bearer {token}"
    })

    assert resp.status_code == 200

    data = resp.get_json()["data"]
    assert "user_id" in data
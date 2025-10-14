
def test_me_required_auth(client):
    resp = client.get("api/users/me")
    assert resp.status_code == 401

def test_me_with_valid_token(client):
    # Use existing test user from auth_client fixture
    from app.models import User
    from app.extensions import db
    
    # Find existing user or create one
    user = User.query.filter_by(email="test@example.com").first()
    if not user:
        from app.services.auth_service import AuthService
        user = User(email="test@example.com", username="testuser", hash=AuthService.hash_password("password001"))
        db.session.add(user)
        db.session.commit()
    
    login_resp = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password001",
    })

    assert login_resp.status_code == 200
    token = login_resp.get_json()["access_token"]

    resp = client.get("/api/users/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert "user_id" in data
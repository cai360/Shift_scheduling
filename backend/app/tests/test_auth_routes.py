
def test_me_required_auth(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401

def test_register_returns_created_user(api_client):
    resp = api_client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "password001",
    })

    assert resp.status_code == 201
    data = api_client.data(resp)
    assert data["email"] == "new@example.com"
    assert data["username"] == "newuser"
    assert "id" in data

def test_login_returns_tokens(client, user_factory):
    user_factory(email="test@example.com", password="password001")
    login_resp = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password001",
    })
    assert login_resp.status_code == 200
    data = login_resp.get_json()["data"]
    assert data["access_token"]
    assert data["refresh_token"]

def test_me_with_valid_token(api_client, login_as):
    _, tokens = login_as()

    resp = api_client.get("/api/auth/me", token=tokens["access_token"])

    assert resp.status_code == 200
    data = api_client.data(resp)
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_refresh_returns_new_access_token(api_client, login_as):
    _, tokens = login_as()

    resp = api_client.post("/api/auth/refresh", json={
        "refresh_token": tokens["refresh_token"],
    })

    assert resp.status_code == 200
    data = api_client.data(resp)
    assert data["access_token"]

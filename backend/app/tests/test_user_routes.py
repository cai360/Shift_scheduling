from uuid import uuid4

def unique_email():
    return f"u_{uuid4().hex[:8]}@example.com"

def test_users_ping(client):
    resp = client.get("/api/users/ping")
    assert resp.status_code == 200
    assert resp.get_json() == {"message": "ping"}

def test_create_user_201(client):
    payload = {
        "email": unique_email(),
        "username": "tester",
        "password": "password001"
    }
    resp = client.post("/api/users", json=payload)
    assert resp.status_code in (200, 201)
    data = resp.get_json()
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]
    assert "password" not in data
    assert "password_hash" not in data

def test_get_user_200(client):
    payload = {"email": unique_email(), "username": "testName", "password": "Password001"}
    created = client.post("/api/users", json=payload).get_json()
    uid = created["id"]

    resp = client.get(f"/api/users/{uid}")
    assert resp.status_code == 200
    got = resp.get_json()
    assert got["id"] == uid
    assert got["email"] == payload["email"]
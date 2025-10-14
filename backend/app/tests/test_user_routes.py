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

def test_get_user_200(auth_client):
    payload = {"email": unique_email(), "username": "testName", "password": "Password001"}
    created = auth_client.post("/api/users", json=payload).get_json()
    uid = created["id"]

    resp = auth_client.get(f"/api/users/{uid}")
    assert resp.status_code == 200
    got = resp.get_json()
    assert got["id"] == uid
    assert got["email"] == payload["email"]


def test_patch_user_email(auth_client):
    created = auth_client.post("/api/users", json = {"email": unique_email(), "username": "username1", "password": "PassWord001"}).get_json()
    uid = created["id"]
    new_email = unique_email()

    resp = auth_client.patch(f"/api/users/{uid}", json={"email": new_email})
    assert resp.status_code == 200
    updated = resp.get_json()
    assert updated["email"] == new_email


def test_delete_user_200_soft_delete(auth_client):
    created = auth_client.post("/api/users", json={
        "email": unique_email(), "username": "deleteME", "password": "PassWord001"}).get_json()
    uid = created["id"]

    resp = auth_client.delete(f"/api/users/{uid}")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["active"] in (False, 0, None)
    

def test_create_user_duplicate_email_400(client):
    email = unique_email()
    r1 = client.post("/api/users", json={"email": email, "username": "dup1", "password": "Password123"})
    assert r1.status_code in (200, 201)

    r2 = client.post("/api/users", json={"email": email, "username": "dup2", "password": "Password123"})
    assert r2.status_code == 400
    
    err = r2.get_json()
    assert "error" in err
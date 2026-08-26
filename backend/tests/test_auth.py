from tests.conftest import auth_headers, login_user, register_user


def test_register_creates_user(client):
    resp = register_user(client, "alice@example.com")
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert body["role"] == "candidate"
    assert "hashed_password" not in body


def test_register_duplicate_email_fails(client):
    register_user(client, "bob@example.com")
    resp = register_user(client, "bob@example.com")
    assert resp.status_code == 400


def test_login_success(client):
    register_user(client, "carol@example.com")
    resp = client.post(
        "/auth/login", data={"username": "carol@example.com", "password": "password123"}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password_fails(client):
    register_user(client, "dave@example.com")
    resp = client.post(
        "/auth/login", data={"username": "dave@example.com", "password": "wrongpass"}
    )
    assert resp.status_code == 401


def test_me_requires_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client):
    register_user(client, "erin@example.com")
    token = login_user(client, "erin@example.com")
    resp = client.get("/auth/me", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["email"] == "erin@example.com"

def test_login_success(client):
    resp = client.post(
        "/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    # Check that we reached home/dashboard
    assert b"home" in resp.data.lower() or b"dashboard" in resp.data.lower() \
        or b"budget" in resp.data.lower()


def test_login_failure(client):
    resp = client.post(
        "/login",
        data={"username": "admin", "password": "wrongpassword"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    # Should remain on login page
    assert b"login" in resp.data.lower() or b"sign in" in resp.data.lower()


def test_home_requires_login(client):
    resp = client.get("/home", follow_redirects=False)
    assert resp.status_code in (301, 302)
    assert "/login" in resp.headers["Location"]

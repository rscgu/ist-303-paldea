def test_home_page_loads_for_logged_in_user(logged_in_client):
    resp = logged_in_client.get("/home")
    assert resp.status_code == 200
    assert (
        b"budget" in resp.data.lower()
        or b"transaction" in resp.data.lower()
        or b"dashboard" in resp.data.lower()
    )

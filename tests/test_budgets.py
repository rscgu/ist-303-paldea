def test_set_category_budget(logged_in_client):
    resp = logged_in_client.post(
        "/set_category_budget",
        data={
            "category": 1,
            "budget_amount": "150.00",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    # Should return to home/dashboard
    assert b"budget" in resp.data.lower() or b"progress" in resp.data.lower()

def test_add_transaction(logged_in_client):
    resp = logged_in_client.post(
        "/add_transaction",
        data={
            "description": "Unit Test Expense",
            "amount": "25.00",
            "type": "expense",
            "category": 1,
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    # After adding a transaction, user is redirected to home page
    assert b"budget" in resp.data.lower() or b"transaction" in resp.data.lower()

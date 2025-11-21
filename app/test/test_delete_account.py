def test_delete_account_success(client):
    response = client.delete("/accounts/me", json={
        "reason": "privacy"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_delete_account_no_reason(client):
    response = client.delete("/accounts/me", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

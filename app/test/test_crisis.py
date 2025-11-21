def test_crisis_escalation_valid(client):
    response = client.post("/crisis/escalate", json={
        "user_id": 1,
        "content_snippet": "I feel unsafe."
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "open"

def test_crisis_without_user(client):
    response = client.post("/crisis/escalate", json={
        "content_snippet": "Someone flagged this."
    })
    assert response.status_code == 200

def test_crisis_too_long(client):
    long_text = "a" * 5000
    response = client.post("/crisis/escalate", json={
        "content_snippet": long_text
    })
    assert response.status_code in (200, 422, 400)

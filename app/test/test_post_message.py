from app import models

def test_create_valid_post(client):
    response = client.post("/posts/", json={
        "group_id": 1,
        "content": "Hello everyone!"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Hello everyone!"
    assert data["status"] == "active"


def test_empty_content_post(client):
    response = client.post("/posts/", json={
        "group_id": 1,
        "content": ""
    })
    assert response.status_code == 422


def test_post_without_group(client):
    response = client.post("/posts/", json={
        "content": "No group id"
    })
    assert response.status_code == 200


def test_post_too_long(client):
    long_text = "a" * 5000
    response = client.post("/posts/", json={
        "group_id": 1,
        "content": long_text
    })
    assert response.status_code in (400, 422)


def test_banned_user_cannot_post(client, db):
    # ban first user
    user = db.query(models.User).first()
    user.is_banned = True
    db.commit()

    response = client.post("/posts/", json={
        "group_id": 1,
        "content": "Hello but banned"
    })
    assert response.status_code == 403

"""
Tests for post message functionality.
"""
import pytest
from app import models


def test_create_valid_post(client, auth_headers, db):
    """Test creating a valid post returns success."""
    response = client.post(
        "/posts/",
        json={
            "group_id": 1,
            "content": "Hello everyone!",
            "posttime": 1234567890.0
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Hello everyone!"
    assert data["status"] == "active"


def test_empty_content_post(client, auth_headers):
    """Test that empty content returns validation error."""
    response = client.post(
        "/posts/",
        json={
            "group_id": 1,
            "content": "",
            "posttime": 1234567890.0
        },
        headers=auth_headers
    )
    assert response.status_code == 422


def test_post_without_group(client, auth_headers):
    """Test posting without group_id is allowed."""
    response = client.post(
        "/posts/",
        json={
            "content": "No group id",
            "posttime": 1234567890.0
        },
        headers=auth_headers
    )
    assert response.status_code == 200


def test_post_requires_authentication(client):
    """Test that posting without auth returns 401."""
    response = client.post(
        "/posts/",
        json={
            "group_id": 1,
            "content": "Hello",
            "posttime": 1234567890.0
        }
    )
    assert response.status_code == 401


def test_banned_user_cannot_post(client, db, auth_headers, test_user):
    """Test that banned users cannot create posts."""
    # Ban the test user
    test_user.is_banned = True
    db.commit()

    response = client.post(
        "/posts/",
        json={
            "group_id": 1,
            "content": "Hello but banned",
            "posttime": 1234567890.0
        },
        headers=auth_headers
    )
    assert response.status_code == 403

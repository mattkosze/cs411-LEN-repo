"""
Tests for crisis escalation functionality.
"""
import pytest


def test_crisis_escalation_valid(client, auth_headers):
    """Test valid crisis escalation request."""
    response = client.post(
        "/crisis/escalate",
        json={
            "user_id": 1,
            "content_snip": "I feel unsafe."
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "open"


def test_crisis_without_user(client, auth_headers):
    """Test crisis escalation without specific user."""
    response = client.post(
        "/crisis/escalate",
        json={
            "content_snip": "Someone flagged this."
        },
        headers=auth_headers
    )
    assert response.status_code == 200


def test_crisis_requires_authentication(client):
    """Test that crisis escalation requires authentication."""
    response = client.post(
        "/crisis/escalate",
        json={
            "content_snip": "Test content."
        }
    )
    assert response.status_code == 401


def test_crisis_content_truncated(client, auth_headers):
    """Test that long content is handled (truncated in audit log)."""
    long_text = "a" * 200
    response = client.post(
        "/crisis/escalate",
        json={
            "content_snip": long_text
        },
        headers=auth_headers
    )
    # Should succeed - content is truncated in service layer
    assert response.status_code == 200

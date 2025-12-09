"""
Tests for account deletion functionality.
"""
import pytest
import json as json_lib


def test_delete_account_success(client, auth_headers):
    """Test successful account deletion."""
    response = client.request(
        "DELETE",
        "/accounts/me/",
        content=json_lib.dumps({"reason": "privacy concerns"}),
        headers={**auth_headers, "Content-Type": "application/json"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_delete_account_empty_reason(client, auth_headers):
    """Test account deletion with empty reason still works."""
    response = client.request(
        "DELETE",
        "/accounts/me/",
        content=json_lib.dumps({"reason": ""}),
        headers={**auth_headers, "Content-Type": "application/json"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_delete_account_requires_auth(client):
    """Test that account deletion requires authentication."""
    response = client.request(
        "DELETE",
        "/accounts/me/",
        content=json_lib.dumps({"reason": "test"}),
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 401

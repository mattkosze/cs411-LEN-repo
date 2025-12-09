# app/test/test_routers_endpoints.py
"""Tests for router endpoints using mocked dependencies."""

from types import SimpleNamespace
import pytest

from app.routers import accounts, boards, moderation, posts
from app import models
from app.test.test_helpers import FakeDB, FakeQuery


# ---------- accounts.py tests ----------

def test_register_creates_token(monkeypatch):
    fake_db = FakeDB()
    fake_user = SimpleNamespace(id=123)

    def fake_register_user(db, user_data):
        assert db is fake_db
        return fake_user

    def fake_create_access_token(data):
        # We assert the ID made it into the token payload
        assert data == {"sub": str(fake_user.id)}
        return "fake-token"

    monkeypatch.setattr(accounts.account_service, "register_user", fake_register_user)
    monkeypatch.setattr(accounts.account_service, "create_access_token", fake_create_access_token)

    # We can pass any object as user_data; the router just forwards it
    result = accounts.register(user_data=SimpleNamespace(), db=fake_db)

    assert result["access_token"] == "fake-token"
    assert result["token_type"] == "bearer"


def test_login_returns_token(monkeypatch):
    fake_db = FakeDB()
    fake_user = SimpleNamespace(id=42)

    def fake_authenticate_user(db, email, password):
        assert db is fake_db
        assert email == "user@example.com"
        assert password == "secret"
        return fake_user

    def fake_create_access_token(data):
        assert data == {"sub": str(fake_user.id)}
        return "login-token"

    monkeypatch.setattr(accounts.account_service, "authenticate_user", fake_authenticate_user)
    monkeypatch.setattr(accounts.account_service, "create_access_token", fake_create_access_token)

    credentials = SimpleNamespace(email="user@example.com", password="secret")
    result = accounts.login(credentials=credentials, db=fake_db)

    assert result["access_token"] == "login-token"
    assert result["token_type"] == "bearer"


def test_logout_returns_message():
    result = accounts.logout()
    assert result == {"message": "Successfully logged out"}


def test_get_all_users_uses_db_query():
    fake_users = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
    fake_db = FakeDB(result_list=fake_users)

    result = accounts.get_all_users(db=fake_db)
    assert result == fake_users


def test_get_current_user_info_returns_user():
    current_user = SimpleNamespace(id=99, email="me@example.com")
    result = accounts.get_current_user_info(db=None, current_user=current_user)
    assert result is current_user


def test_delete_my_account_calls_service(monkeypatch):
    fake_db = FakeDB()
    current_user = SimpleNamespace(id=5)
    called = {}

    def fake_delete_account(db, user, reason):
        called["args"] = (db, user, reason)
        return {"success": True, "user_id": user.id, "reason": reason}

    monkeypatch.setattr(accounts.account_service, "delete_account", fake_delete_account)

    req = accounts.DeleteAccountRequest(reason="no longer needed")
    result = accounts.delete_my_account(req=req, db=fake_db, current_user=current_user)

    assert result["success"] is True
    assert called["args"][0] is fake_db
    assert called["args"][1] is current_user
    assert called["args"][2] == "no longer needed"


# ---------- boards.py tests ----------

def test_get_boards_calls_service(monkeypatch):
    fake_db = FakeDB()
    current_user = SimpleNamespace(id=1)
    fake_boards = [SimpleNamespace(id=10), SimpleNamespace(id=11)]

    def fake_list_boards(db):
        assert db is fake_db
        return fake_boards

    monkeypatch.setattr(boards.board_service, "list_boards", fake_list_boards)

    result = boards.get_boards(db=fake_db, current_user=current_user)
    assert result == fake_boards


def test_create_board_as_moderator(monkeypatch):
    fake_db = FakeDB()
    current_user = SimpleNamespace(id=1, role=models.UserRole.MODERATOR)
    data = SimpleNamespace(name="Test Board")

    def fake_create_board(db, d):
        assert db is fake_db
        assert d is data
        return SimpleNamespace(id=123, name=d.name)

    monkeypatch.setattr(boards.board_service, "create_board", fake_create_board)

    result = boards.create_board(data=data, db=fake_db, current_user=current_user)
    assert result.id == 123
    assert result.name == "Test Board"


def test_create_board_forbidden_for_regular_user():
    fake_db = FakeDB()
    # Some non-moderator, non-admin role
    current_user = SimpleNamespace(id=1, role=models.UserRole.USER)
    data = SimpleNamespace()

    with pytest.raises(Exception):  # HTTPException underneath
        boards.create_board(data=data, db=fake_db, current_user=current_user)


# ---------- moderation.py tests ----------

def test_get_reports_without_status(monkeypatch):
    fake_reports = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
    fake_db = FakeDB(result_list=fake_reports)
    current_user = SimpleNamespace(id=1)

    def fake_require_moderator(user):
        # Ensure dependency is called
        assert user is current_user
        return SimpleNamespace(id=999)

    monkeypatch.setattr(moderation, "require_moderator", fake_require_moderator)

    result = moderation.get_reports(status=None, db=fake_db, current_user=current_user)
    assert result == fake_reports


def test_get_reports_with_invalid_status(monkeypatch):
    # This should hit the ValueError branch but still succeed
    fake_reports = [SimpleNamespace(id=3)]
    fake_db = FakeDB(result_list=fake_reports)
    current_user = SimpleNamespace(id=1)

    def fake_require_moderator(user):
        return SimpleNamespace(id=999)

    monkeypatch.setattr(moderation, "require_moderator", fake_require_moderator)

    result = moderation.get_reports(status="not-a-real-status", db=fake_db, current_user=current_user)
    assert result == fake_reports


def test_determine_action_calls_service(monkeypatch):
    fake_db = FakeDB()
    current_user = SimpleNamespace(id=1)

    def fake_require_moderator(user):
        return SimpleNamespace(id=999)

    fake_report = SimpleNamespace(
        id=10,
        reporting_user_id=1,
        reported_user_id=2,
        post_id=3,
        reason=models.ReportReason.SPAM,
        details="test details",
        is_crisis=False,
        status=models.ReportStatus.RESOLVED,
        resolution_impact="dismissed",
        created_at=1234567890.0,
        resolved_at=1234567891.0
    )

    def fake_determine_action(db, moderator, data):
        assert db is fake_db
        return fake_report

    monkeypatch.setattr(moderation, "require_moderator", fake_require_moderator)
    monkeypatch.setattr(moderation.moderation_service, "determine_action", fake_determine_action)

    data = SimpleNamespace()
    result = moderation.determine_action(data=data, db=fake_db, current_user=current_user)
    assert result.report.id == 10


def test_moderation_delete_post_calls_service(monkeypatch):
    fake_db = FakeDB()
    current_user = SimpleNamespace(id=1)
    fake_post = SimpleNamespace(id=7, status=models.PostStatus.DELETED)

    def fake_require_moderator(user):
        return SimpleNamespace(id=999)

    def fake_delete_post(db, moderator, post_id, reason, report_id=None):
        assert post_id == 7
        assert reason == "spam"
        return fake_post

    monkeypatch.setattr(moderation, "require_moderator", fake_require_moderator)
    monkeypatch.setattr(moderation.moderation_service, "delete_post", fake_delete_post)

    result = moderation.delete_post(
        post_id=7,
        reason="spam",
        report_id=None,
        db=fake_db,
        current_user=current_user,
    )
    assert result.success is True
    assert result.post_id == 7
    assert result.status == models.PostStatus.DELETED


def test_moderation_delete_account_user_found(monkeypatch):
    fake_user = SimpleNamespace(id=5)
    # FakeDB that returns fake_user on first()
    fake_db = FakeDB(first_result=fake_user)
    current_user = SimpleNamespace(id=1)

    def fake_require_moderator(user):
        return SimpleNamespace(id=999)

    def fake_delete_account(db, user, reason):
        assert user is fake_user
        return {"deleted_id": user.id, "reason": reason}

    monkeypatch.setattr(moderation, "require_moderator", fake_require_moderator)
    monkeypatch.setattr(moderation.account_service, "delete_account", fake_delete_account)

    result = moderation.delete_account(
        user_id=5,
        reason="violation",
        report_id=None,
        db=fake_db,
        current_user=current_user,
    )
    assert result["deleted_id"] == 5
    assert result["reason"] == "violation"


def test_moderation_delete_account_user_not_found(monkeypatch):
    # FakeDB that returns None on first()
    fake_db = FakeDB(first_result=None)
    current_user = SimpleNamespace(id=1)

    def fake_require_moderator(user):
        return SimpleNamespace(id=999)

    monkeypatch.setattr(moderation, "require_moderator", fake_require_moderator)

    with pytest.raises(Exception):  # HTTPException
        moderation.delete_account(
            user_id=999,
            reason="whatever",
            db=fake_db,
            current_user=current_user,
        )


# ---------- posts.py tests ----------

def test_get_posts_no_group(fake_posts=None):
    if fake_posts is None:
        fake_posts = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
    fake_db = FakeDB(result_list=fake_posts)
    current_user = SimpleNamespace(id=1)

    result = posts.get_posts(group_id=None, db=fake_db, current_user=current_user)
    assert result == fake_posts


def test_get_posts_with_group():
    fake_posts = [SimpleNamespace(id=10)]
    fake_db = FakeDB(result_list=fake_posts)
    current_user = SimpleNamespace(id=1)

    # Just ensure it runs with a group_id argument
    result = posts.get_posts(group_id=123, db=fake_db, current_user=current_user)
    assert result == fake_posts


def test_post_message_calls_service(monkeypatch):
    fake_db = FakeDB()
    current_user = SimpleNamespace(id=1)
    data = SimpleNamespace(text="hello")
    fake_post = SimpleNamespace(id=7, text="hello")

    def fake_post_message(db, user, d):
        assert db is fake_db
        assert user is current_user
        assert d is data
        return fake_post

    monkeypatch.setattr(posts.messaging_service, "post_message", fake_post_message)

    result = posts.post_message(data=data, db=fake_db, current_user=current_user)
    assert result is fake_post


def test_posts_delete_post_calls_service(monkeypatch):
    fake_db = FakeDB()
    current_user = SimpleNamespace(id=1)
    fake_post = SimpleNamespace(id=5, status=models.PostStatus.DELETED)

    def fake_delete_post(db, user, post_id):
        assert post_id == 5
        return fake_post

    monkeypatch.setattr(posts.messaging_service, "delete_post", fake_delete_post)

    result = posts.delete_post(post_id=5, db=fake_db, current_user=current_user)
    assert result.success is True
    assert result.post_id == 5
    assert result.status == models.PostStatus.DELETED


def test_report_post_calls_service(monkeypatch):
    fake_db = FakeDB()
    current_user = SimpleNamespace(id=1)
    data = SimpleNamespace(reason="spam")
    fake_report = SimpleNamespace(id=3, reason="spam")

    def fake_create_report(db, user, post_id, d):
        assert post_id == 42
        assert d is data
        return fake_report

    monkeypatch.setattr(posts.report_service, "create_report", fake_create_report)

    result = posts.report_post(
        post_id=42,
        data=data,
        db=fake_db,
        current_user=current_user,
    )
    assert result is fake_report

"""Tests for service layer functions."""
import datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app import models
from app.services import (
    account_service,
    board_service,
    crisis_service,
    messaging_service,
    moderation_service,
    report_service,
)
from app.test.test_helpers import FakeQuery, FakeSession


# ---------- account_service tests ----------

def test_hash_and_verify_password_round_trip():
    pw = "supersafe"
    hashed = account_service.hash_password(pw)
    assert hashed != pw
    assert account_service.verify_password(pw, hashed) is True


def test_verify_password_with_empty_hash():
    assert account_service.verify_password("somepw", "") is False


def test_register_user_success_creates_user():
    db = FakeSession({models.User: []})
    user_data = SimpleNamespace(
        email="new@example.com",
        password="pw123",
        display_name="New User",
    )

    user = account_service.register_user(db, user_data)

    assert user.email == "new@example.com"
    assert user.display_name == "New User"
    assert user.is_anonymous is False
    assert user.is_active is True
    # user got added to "db"
    assert db.data[models.User][0] is user


def test_register_user_existing_email_raises():
    existing = models.User()
    existing.email = "taken@example.com"
    db = FakeSession({models.User: [existing]})
    user_data = SimpleNamespace(
        email="taken@example.com",
        password="pw",
        display_name="Dup",
    )

    with pytest.raises(HTTPException) as exc:
        account_service.register_user(db, user_data)
    assert exc.value.status_code == 400


def test_authenticate_user_not_found_raises():
    db = FakeSession({models.User: []})
    with pytest.raises(HTTPException) as exc:
        account_service.authenticate_user(db, "nope@example.com", "pw")
    assert exc.value.status_code == 401


def test_authenticate_user_inactive_raises():
    user = models.User()
    user.email = "inactive@example.com"
    user.is_active = False
    user.hashed_password = account_service.hash_password("pw")

    db = FakeSession({models.User: [user]})

    with pytest.raises(HTTPException) as exc:
        account_service.authenticate_user(db, user.email, "pw")
    assert exc.value.status_code == 403


def test_authenticate_user_bad_password_raises():
    user = models.User()
    user.email = "user@example.com"
    user.is_active = True
    user.hashed_password = account_service.hash_password("correctpw")

    db = FakeSession({models.User: [user]})

    with pytest.raises(HTTPException) as exc:
        account_service.authenticate_user(db, user.email, "wrongpw")
    assert exc.value.status_code == 401


def test_authenticate_user_success():
    user = models.User()
    user.email = "user@example.com"
    user.is_active = True
    user.hashed_password = account_service.hash_password("correctpw")

    db = FakeSession({models.User: [user]})

    result = account_service.authenticate_user(db, user.email, "correctpw")
    assert result is user


def test_create_access_token_returns_string():
    token = account_service.create_access_token({"sub": "123"})
    assert isinstance(token, str)
    assert token  # not empty


def test_delete_account_marks_user_deleted_and_logs():
    user = models.User()
    user.id = 1
    user.display_name = "Active"
    user.email = "user@example.com"
    user.hashed_password = account_service.hash_password("pw")
    user.is_anonymous = False
    user.is_active = True

    db = FakeSession({models.User: [user], models.AuditLogEntry: []})

    result = account_service.delete_account(db, user, "no longer needed")

    assert result.success is True
    assert user.display_name == "Deleted User"
    assert user.email is None
    assert user.hashed_password is None
    assert user.is_anonymous is True
    assert user.is_active is False
    # audit log created
    assert len(db.data[models.AuditLogEntry]) == 1


# ---------- board_service tests ----------

def test_list_boards_returns_all():
    b1 = models.ConditionBoard()
    b1.id = 1
    b2 = models.ConditionBoard()
    b2.id = 2
    db = FakeSession({models.ConditionBoard: [b1, b2]})

    result = board_service.list_boards(db)

    assert result == [b1, b2]


def test_create_board_success():
    db = FakeSession({models.ConditionBoard: []})
    data = SimpleNamespace(name="New Board", description="desc")

    board = board_service.create_board(db, data)

    assert board.name == "New Board"
    assert board in db.data[models.ConditionBoard]


def test_create_board_existing_name_raises():
    existing = models.ConditionBoard()
    existing.name = "Existing"
    db = FakeSession({models.ConditionBoard: [existing]})
    data = SimpleNamespace(name="Existing", description="x")

    with pytest.raises(HTTPException) as exc:
        board_service.create_board(db, data)
    assert exc.value.status_code == 400


def test_seed_initial_boards_when_empty_creates_them():
    db = FakeSession({models.ConditionBoard: []})
    board_service.seed_initial_boards(db)
    assert len(db.data[models.ConditionBoard]) == len(board_service.INITIAL_BOARDS)


def test_seed_initial_boards_when_not_empty_does_nothing():
    existing = models.ConditionBoard()
    existing.name = "Already here"
    db = FakeSession({models.ConditionBoard: [existing]})
    board_service.seed_initial_boards(db)
    # still only the existing board
    assert len(db.data[models.ConditionBoard]) == 1


# ---------- crisis_service tests ----------

def test_escalate_crisis_creates_ticket_and_audit():
    db = FakeSession({models.CrisisTicket: [], models.AuditLogEntry: []})
    data = SimpleNamespace(
        user_id=1,
        report_id=2,
        content_snip="urgent situation",
    )

    ticket = crisis_service.escalate_crisis(db, data)

    assert isinstance(ticket, models.CrisisTicket)
    assert len(db.data[models.CrisisTicket]) == 1
    assert len(db.data[models.AuditLogEntry]) == 1


# ---------- messaging_service tests ----------

def test_post_message_banned_user_raises():
    db = FakeSession()
    author = SimpleNamespace(id=1, is_banned=True)
    data = SimpleNamespace(group_id=1, content="hi", posttime=datetime.datetime.utcnow())

    with pytest.raises(HTTPException) as exc:
        messaging_service.post_message(db, author, data)
    assert exc.value.status_code == 403


def test_post_message_creates_post():
    db = FakeSession({models.Post: []})
    author = SimpleNamespace(id=1, is_banned=False)
    now = datetime.datetime.utcnow()
    data = SimpleNamespace(group_id=2, content="hello", posttime=now)

    post = messaging_service.post_message(db, author, data)

    assert isinstance(post, models.Post)
    assert post in db.data[models.Post]
    assert post.author_id == author.id
    assert post.group_id == 2
    assert post.content == "hello"


def test_delete_post_not_found_raises():
    db = FakeSession({models.Post: []})
    user = SimpleNamespace(id=1)

    with pytest.raises(HTTPException) as exc:
        messaging_service.delete_post(db, user, post_id=123)
    assert exc.value.status_code == 404


def test_delete_post_wrong_author_raises():
    post = models.Post()
    post.id = 1
    post.author_id = 2
    post.status = models.PostStatus.ACTIVE
    db = FakeSession({models.Post: [post]})
    user = SimpleNamespace(id=1)

    with pytest.raises(HTTPException) as exc:
        messaging_service.delete_post(db, user, post_id=1)
    assert exc.value.status_code == 403


def test_delete_post_already_deleted_raises():
    post = models.Post()
    post.id = 1
    post.author_id = 1
    post.status = models.PostStatus.DELETED
    db = FakeSession({models.Post: [post]})
    user = SimpleNamespace(id=1)

    with pytest.raises(HTTPException) as exc:
        messaging_service.delete_post(db, user, post_id=1)
    assert exc.value.status_code == 400


def test_delete_post_success_marks_deleted():
    post = models.Post()
    post.id = 1
    post.author_id = 1
    post.status = models.PostStatus.ACTIVE
    db = FakeSession({models.Post: [post]})
    user = SimpleNamespace(id=1)

    result = messaging_service.delete_post(db, user, post_id=1)

    assert result is post
    assert post.status == models.PostStatus.DELETED


# ---------- moderation_service tests ----------

def test_determine_action_invalid_action_raises():
    db = FakeSession()
    moderator = SimpleNamespace(id=1)
    data = SimpleNamespace(action="not-valid", report_id=1, mod_note=None)

    with pytest.raises(HTTPException) as exc:
        moderation_service.determine_action(db, moderator, data)
    assert exc.value.status_code == 400


def test_determine_action_missing_report_raises():
    db = FakeSession({models.Report: []})
    moderator = SimpleNamespace(id=1)
    data = SimpleNamespace(action="warn", report_id=1, mod_note=None)

    with pytest.raises(HTTPException) as exc:
        moderation_service.determine_action(db, moderator, data)
    assert exc.value.status_code == 404


def test_determine_action_crisis_report_raises():
    report = models.Report()
    report.id = 1
    report.is_crisis = True
    db = FakeSession({models.Report: [report]})
    moderator = SimpleNamespace(id=1)
    data = SimpleNamespace(action="warn", report_id=1, mod_note=None)

    with pytest.raises(HTTPException) as exc:
        moderation_service.determine_action(db, moderator, data)
    assert exc.value.status_code == 400


def test_determine_action_ban_resolves_report_and_bans_user():
    report = models.Report()
    report.id = 1
    report.is_crisis = False
    report.status = models.ReportStatus.OPEN
    report.resolution_impact = None
    report.reported_user_id = 10

    user = models.User()
    user.id = 10
    user.is_banned = False

    db = FakeSession({
        models.Report: [report],
        models.User: [user],
        models.AuditLogEntry: [],
    })

    moderator = SimpleNamespace(id=1)
    data = SimpleNamespace(action="ban", report_id=1, mod_note="bad behavior")

    result = moderation_service.determine_action(db, moderator, data)

    assert result is report
    assert report.status == models.ReportStatus.RESOLVED
    assert report.resolution_impact == "ban"
    assert user.is_banned is True
    assert len(db.data[models.AuditLogEntry]) == 1


def test_moderation_delete_post_not_found_raises():
    db = FakeSession({models.Post: []})
    moderator = SimpleNamespace(id=1)

    with pytest.raises(HTTPException) as exc:
        moderation_service.delete_post(db, moderator, post_id=1, reason="x")
    assert exc.value.status_code == 404


def test_moderation_delete_post_already_deleted_raises():
    post = models.Post()
    post.id = 1
    post.status = models.PostStatus.DELETED
    db = FakeSession({models.Post: [post]})
    moderator = SimpleNamespace(id=1)

    with pytest.raises(HTTPException) as exc:
        moderation_service.delete_post(db, moderator, post_id=1, reason="x")
    assert exc.value.status_code == 400


def test_moderation_delete_post_success_marks_deleted_and_logs():
    post = models.Post()
    post.id = 1
    post.status = models.PostStatus.ACTIVE
    db = FakeSession({models.Post: [post], models.AuditLogEntry: []})
    moderator = SimpleNamespace(id=1)

    result = moderation_service.delete_post(db, moderator, post_id=1, reason="spam")

    assert result is post
    assert post.status == models.PostStatus.DELETED
    assert len(db.data[models.AuditLogEntry]) == 1


# ---------- report_service tests ----------

def _make_post(id_, author_id, status):
    post = models.Post()
    post.id = id_
    post.author_id = author_id
    post.status = status
    return post


def test_create_report_post_not_found_raises():
    db = FakeSession({models.Post: []})
    reporter = models.User()
    reporter.id = 1
    data = SimpleNamespace(reason=models.ReportReason.SPAM, details=None)

    with pytest.raises(HTTPException) as exc:
        report_service.create_report(db, reporter, post_id=1, data=data)
    assert exc.value.status_code == 404


def test_create_report_inactive_post_raises():
    post = _make_post(1, author_id=2, status=models.PostStatus.DELETED)
    db = FakeSession({models.Post: [post]})
    reporter = models.User()
    reporter.id = 1
    data = SimpleNamespace(reason=models.ReportReason.SPAM, details=None)

    with pytest.raises(HTTPException) as exc:
        report_service.create_report(db, reporter, post_id=1, data=data)
    assert exc.value.status_code == 400


def test_create_report_self_report_raises():
    post = _make_post(1, author_id=1, status=models.PostStatus.ACTIVE)
    db = FakeSession({models.Post: [post]})
    reporter = models.User()
    reporter.id = 1
    data = SimpleNamespace(reason=models.ReportReason.SPAM, details=None)

    with pytest.raises(HTTPException) as exc:
        report_service.create_report(db, reporter, post_id=1, data=data)
    assert exc.value.status_code == 400


def test_create_report_existing_open_report_raises():
    post = _make_post(1, author_id=2, status=models.PostStatus.ACTIVE)
    existing = models.Report()
    existing.id = 1
    existing.reporting_user_id = 1
    existing.post_id = 1
    existing.status = models.ReportStatus.OPEN

    db = FakeSession({
        models.Post: [post],
        models.Report: [existing],
    })

    reporter = models.User()
    reporter.id = 1
    data = SimpleNamespace(reason=models.ReportReason.SPAM, details=None)

    with pytest.raises(HTTPException) as exc:
        report_service.create_report(db, reporter, post_id=1, data=data)
    assert exc.value.status_code == 400


def test_create_report_non_crisis_success_no_ticket():
    post = _make_post(1, author_id=2, status=models.PostStatus.ACTIVE)
    db = FakeSession({
        models.Post: [post],
        models.Report: [],
        models.CrisisTicket: [],
        models.AuditLogEntry: [],
    })

    reporter = models.User()
    reporter.id = 1
    data = SimpleNamespace(reason=models.ReportReason.SPAM, details="spam here")

    report = report_service.create_report(db, reporter, post_id=1, data=data)

    assert isinstance(report, models.Report)
    assert report.is_crisis is False
    assert len(db.data[models.CrisisTicket]) == 0


def test_create_report_crisis_creates_ticket_and_audit():
    post = _make_post(1, author_id=2, status=models.PostStatus.ACTIVE)
    db = FakeSession({
        models.Post: [post],
        models.Report: [],
        models.CrisisTicket: [],
        models.AuditLogEntry: [],
    })

    reporter = models.User()
    reporter.id = 1
    data = SimpleNamespace(reason=models.ReportReason.CRISIS, details="urgent")

    report = report_service.create_report(db, reporter, post_id=1, data=data)

    assert isinstance(report, models.Report)
    assert report.is_crisis is True
    assert len(db.data[models.CrisisTicket]) == 1
    assert len(db.data[models.AuditLogEntry]) == 1

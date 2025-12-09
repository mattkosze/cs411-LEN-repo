"""
Test configuration and shared fixtures for pytest.

This module sets up an isolated test database and provides
reusable fixtures for testing.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator

from app.main import app
from app.db import Base, get_db
from app.models import User, UserRole
from app.services.account_service import hash_password, create_access_token


# Create an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """Override the get_db dependency with test database."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def create_test_db():
    """Create all tables fresh for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    """Provide a clean database session for each test."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        # Clean up after each test
        session.rollback()
        session.close()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    """Provide a test client for API testing."""
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def test_user(db: Session) -> User:
    """Create a test user and return it with auth token."""
    user = User(
        email="testuser@example.com",
        hashed_password=hash_password("testpassword"),
        display_name="Test User",
        is_anonymous=False,
        role=UserRole.USER,
        is_banned=False,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def test_moderator(db: Session) -> User:
    """Create a test moderator and return it."""
    user = User(
        email="testmod@example.com",
        hashed_password=hash_password("testpassword"),
        display_name="Test Moderator",
        is_anonymous=False,
        role=UserRole.MODERATOR,
        is_banned=False,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def auth_headers(test_user: User) -> dict:
    """Create authorization headers for a test user."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def mod_auth_headers(test_moderator: User) -> dict:
    """Create authorization headers for a test moderator."""
    token = create_access_token(data={"sub": str(test_moderator.id)})
    return {"Authorization": f"Bearer {token}"}

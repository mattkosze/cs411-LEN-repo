import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from typing import Generator

# Rebuild tables once for all tests
@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture()
def db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c

"""
Shared pytest fixtures for the Urban Heat App test suite.

IMPORTANT: os.environ must be set BEFORE importing the app,
because the API-key middleware and database module read env vars at import time.
"""
import os

# ── Set environment variables BEFORE any app imports ──────────────────────────
os.environ["SECRET_API_KEY"] = "test-key"
os.environ["DATABASE_URL"] = "sqlite:///./test_urban_heat.db"
# Ensure GROQ_API_KEY is unset by default so the AI chat fallback path is tested
os.environ.pop("GROQ_API_KEY", None)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.database import Base, get_db
from backend.main import app


# ── Test database (file-based SQLite, created/destroyed per test) ─────────────
TEST_DATABASE_URL = "sqlite:///./test_urban_heat.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine,
)


def override_get_db():
    """Yield a test database session and roll back on failure."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test, drop them afterwards."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def client():
    """
    FastAPI TestClient with the DB dependency overridden to use the test database.
    Returns a wrapper that auto-injects the X-API-Key header.
    """
    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(app)

    # Store original methods and create wrappers that inject the API key header
    _original_get = test_client.get
    _original_post = test_client.post
    _original_put = test_client.put
    _original_delete = test_client.delete

    def _inject_headers(kwargs):
        headers = kwargs.pop("headers", {}) or {}
        headers.setdefault("X-API-Key", "test-key")
        kwargs["headers"] = headers
        return kwargs

    def get(url, **kwargs):
        return _original_get(url, **_inject_headers(kwargs))

    def post(url, **kwargs):
        return _original_post(url, **_inject_headers(kwargs))

    def put(url, **kwargs):
        return _original_put(url, **_inject_headers(kwargs))

    def delete(url, **kwargs):
        return _original_delete(url, **_inject_headers(kwargs))

    test_client.get = get
    test_client.post = post
    test_client.put = put
    test_client.delete = delete

    yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def db_session():
    """Standalone DB session for tests that need direct DB access."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

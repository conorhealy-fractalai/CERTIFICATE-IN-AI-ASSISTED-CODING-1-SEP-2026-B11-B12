"""Shared pytest fixtures for the ExpenseFlow test suite."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db as db_module
from app.db import get_db
from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """A TestClient backed by a fresh temp-file SQLite DB, isolated per test."""
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False}
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(db_module, "engine", test_engine)
    monkeypatch.setattr(db_module, "SessionLocal", testing_session_local)

    def override_get_db():
        session = testing_session_local()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# NOTE for an Exercise 6+ addendum: any test exercising GET /reports/insights must
# mock app.insights.anthropic.Anthropic (e.g. monkeypatch it to a stub client
# returning a canned Messages response) so tests never make a live network call.
# No such test exists yet, since insights isn't introduced until Exercise 6.

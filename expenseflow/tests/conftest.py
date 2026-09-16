"""Shared pytest fixtures for the ExpenseFlow test suite.

Setting DATABASE_URL before importing app.db/app.main (rather than monkeypatching
their internals afterwards) is what isolates tests from the real expenseflow.db --
app/db.py reads the environment variable once, at import time.
"""

import atexit
import os
import tempfile

import pytest
from fastapi.testclient import TestClient

_fd, _TEST_DB_PATH = tempfile.mkstemp(suffix=".db")
os.close(_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH}"
atexit.register(lambda: os.path.exists(_TEST_DB_PATH) and os.remove(_TEST_DB_PATH))

from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    """A TestClient backed by the shared temp-file SQLite DB, reset per test."""
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


# NOTE for an Exercise 6+ addendum: any test exercising GET /reports/insights must
# mock app.insights.anthropic.Anthropic (e.g. monkeypatch it to a stub client
# returning a canned Messages response) so tests never make a live network call.
# No such test exists yet, since insights isn't introduced until Exercise 6.

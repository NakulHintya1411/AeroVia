"""Shared fixtures.

Tests run against a fresh SQLite file by default. Set TEST_DATABASE_URL to run
them against Postgres instead (CI does this); that database is wiped per test.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import get_settings  # noqa: E402
from db.session import alembic_config, get_engine, init_db, reset_engine  # noqa: E402


@pytest.fixture
def db(tmp_path, monkeypatch):
    test_url = os.environ.get("TEST_DATABASE_URL", "").strip()
    url = test_url or f"sqlite:///{(tmp_path / 'test.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    # Never use a developer's real key from .env in tests.
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("AEROVIA_ALLOW_SIGNUP", "true")
    monkeypatch.delenv("CLAUDE_MODEL", raising=False)
    monkeypatch.delenv("CLAUDE_EFFORT", raising=False)
    get_settings.cache_clear()
    reset_engine()

    if test_url:
        from alembic import command

        engine = get_engine()
        cfg = alembic_config(test_url)
        with engine.begin() as conn:
            cfg.attributes["connection"] = conn
            command.downgrade(cfg, "base")

    init_db()
    yield
    reset_engine()
    get_settings.cache_clear()


@pytest.fixture
def org_user(db):
    """A registered user who owns an organisation."""
    from services import accounts

    return accounts.register("owner@example.com", "Asha Rao", "correct-horse-1", "Pune Route Dev")

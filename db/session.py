"""Engine and session management.

One engine per process. `session_scope()` gives a unit of work that commits on
success and rolls back on any exception.
"""
from __future__ import annotations

import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from config.settings import ROOT, get_settings

_lock = threading.Lock()
_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker[Session]] = None
_migrated_url: Optional[str] = None

MIGRATION_LOCK_KEY = 72_450_001  # arbitrary, fixed id for pg_advisory_xact_lock


def _make_engine(url: str) -> Engine:
    if url.startswith("sqlite"):
        db_path = url.split("///", 1)[-1]
        if db_path and db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(url, connect_args={"check_same_thread": False})

        @event.listens_for(engine, "connect")
        def _sqlite_pragmas(dbapi_conn, _record):  # pragma: no cover - driver hook
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA foreign_keys=ON")
            cur.close()

        return engine
    return create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=5)


def get_engine(url: Optional[str] = None) -> Engine:
    global _engine, _session_factory
    with _lock:
        if _engine is None:
            _engine = _make_engine(url or get_settings().database_url)
            _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)
        return _engine


def reset_engine() -> None:
    """Dispose the engine so the next call reconnects (used by tests)."""
    global _engine, _session_factory, _migrated_url
    with _lock:
        if _engine is not None:
            _engine.dispose()
        _engine = None
        _session_factory = None
        _migrated_url = None


@contextmanager
def session_scope() -> Iterator[Session]:
    get_engine()
    assert _session_factory is not None
    session = _session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def alembic_config(url: Optional[str] = None):
    from alembic.config import Config

    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "migrations"))
    cfg.set_main_option("sqlalchemy.url", (url or get_settings().database_url).replace("%", "%%"))
    return cfg


def init_db() -> None:
    """Bring the schema up to date. Safe to call repeatedly."""
    global _migrated_url
    engine = get_engine()
    url = engine.url.render_as_string(hide_password=False)
    if _migrated_url == url:
        return
    from alembic import command

    cfg = alembic_config(url)
    with engine.begin() as connection:
        if connection.dialect.name == "postgresql":
            # The web app and the API service may start together; make them take
            # turns so only one applies migrations. Released at commit.
            from sqlalchemy import text

            connection.execute(text("SELECT pg_advisory_xact_lock(:k)"), {"k": MIGRATION_LOCK_KEY})
        cfg.attributes["connection"] = connection
        command.upgrade(cfg, "head")
    _migrated_url = url

"""Runtime settings, read from environment variables (and `.env` in development).

Every deploy-specific value lives here so the rest of the code never reads
os.environ directly. See `.env.example` for the full list.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

# Real environment variables win over .env, so production config is never
# overridden by a stray local file.
load_dotenv(ROOT / ".env", override=False)

DEFAULT_SQLITE_PATH = ROOT / "instance" / "aerovia.db"


def _bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def normalise_database_url(url: str) -> str:
    """Point Postgres URLs at the psycopg 3 driver.

    Hosting providers hand out `postgres://` or `postgresql://` URLs; SQLAlchemy
    needs the driver spelled out.
    """
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


@dataclass(frozen=True)
class Settings:
    database_url: str
    anthropic_api_key: str
    claude_model: str
    claude_effort: str
    allow_signup: bool
    environment: str

    @property
    def ai_configured(self) -> bool:
        return bool(self.anthropic_api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    db_url = os.environ.get("DATABASE_URL", "").strip()
    if not db_url:
        db_url = f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"
    return Settings(
        database_url=normalise_database_url(db_url),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", "").strip(),
        claude_model=os.environ.get("CLAUDE_MODEL", "").strip() or "claude-opus-5-5",
        claude_effort=os.environ.get("CLAUDE_EFFORT", "").strip() or "medium",
        allow_signup=_bool("AEROVIA_ALLOW_SIGNUP", True),
        environment=os.environ.get("AEROVIA_ENV", "development").strip() or "development",
    )

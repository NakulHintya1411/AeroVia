from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext

from db import get_engine
from db.models import Base


def test_migrations_match_models(db):
    """Fails if db/models.py changed without a matching Alembic migration."""
    with get_engine().connect() as conn:
        ctx = MigrationContext.configure(conn, opts={"compare_type": True})
        diff = compare_metadata(ctx, Base.metadata)
    assert diff == [], f"Models and migrations differ; run `alembic revision --autogenerate`: {diff}"

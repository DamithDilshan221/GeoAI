"""Shared test fixtures — DB engine, session, and Alembic migration runner.

The ``db_engine`` fixture (session-scoped) runs ``alembic upgrade head`` once
against the native ``geoai_test`` database at the start of the test session,
and ``alembic downgrade base`` at the end.

The ``db_session`` fixture (function-scoped) creates a fresh session per test
and truncates all application tables on teardown.
"""

import os
from collections.abc import Generator

import pytest
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from app.core.config import get_settings

_APP_TABLES = [
    "recommendation_logs",
    "usage_records",
    "facilities",
    "categories",
    "ml_model_versions",
]


@pytest.fixture(scope="session")
def db_engine() -> Generator[Engine, None, None]:
    """Create an engine pointed at geoai_test and run migrations."""
    settings = get_settings()
    test_url = settings.DATABASE_URL_TEST
    engine = create_engine(test_url, echo=False)

    # Set ALEMBIC_DB_URL so env.py routes the migration to the test DB
    os.environ["ALEMBIC_DB_URL"] = test_url

    alembic_cfg = AlembicConfig("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    yield engine

    # Tear down: downgrade to base so tests leave no schema behind
    command.downgrade(alembic_cfg, "base")
    engine.dispose()

    # Clean up the env var override
    os.environ.pop("ALEMBIC_DB_URL", None)


@pytest.fixture()
def db_session(db_engine: Engine) -> Generator[Session, None, None]:
    """Yield a fresh Session per test; truncate all tables on teardown."""
    session = sessionmaker(bind=db_engine)()

    yield session

    session.close()

    # Clean up data in FK-safe order (children first)
    with db_engine.connect() as conn:
        for table in _APP_TABLES:
            conn.execute(text(f"TRUNCATE {table} CASCADE"))
        conn.commit()

"""Alembic environment configuration.

Reads the database URL from ``app.core.config`` so there is a single source
of truth. Supports an ``ALEMBIC_DB_URL`` env-var override so both the dev
and test databases can be migrated with the same tooling::

    # Migrate the dev database (default):
    alembic upgrade head

    # Migrate the test database:
    set ALEMBIC_DB_URL=postgresql+psycopg://postgres:...@localhost:5432/geoai_test
    alembic upgrade head
"""

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.models import Base  # noqa: F401 — ensures all models register

# ── Alembic Config object ────────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# ── Resolve database URL ─────────────────────────────────────────────────
# Priority: ALEMBIC_DB_URL env var → app settings DATABASE_URL
_override_url = os.environ.get("ALEMBIC_DB_URL")
if _override_url:
    _db_url = _override_url
else:
    from app.core.config import get_settings

    _db_url = get_settings().DATABASE_URL

config.set_main_option("sqlalchemy.url", _db_url)


# ── PostGIS exclusion ────────────────────────────────────────────────────
def include_object(
    obj: object,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: object | None,
) -> bool:
    """Exclude PostGIS system tables from autogenerate diffs."""
    return not (type_ == "table" and name == "spatial_ref_sys")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — emit SQL to stdout."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode — connect to a live database."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

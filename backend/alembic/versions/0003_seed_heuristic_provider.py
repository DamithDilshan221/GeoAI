"""seed heuristic provider

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-09 10:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use declared table construct, not ORM import
    ml_model_versions = sa.table(
        "ml_model_versions",
        sa.column("version", sa.String),
        sa.column("algorithm", sa.String),
        sa.column("trained_at", sa.DateTime),
        sa.column("feature_list", sa.JSON),
        sa.column("evaluation_metrics", sa.JSON),
        sa.column("artifact_path", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("notes", sa.String),
    )

    op.execute(
        ml_model_versions.insert().values(
            version="heuristic-v0",
            algorithm=None,
            trained_at=None,
            feature_list=None,
            evaluation_metrics=None,
            artifact_path=None,
            is_active=True,
            notes="Seeded by Phase 10 migration. No trained model has been promoted yet.",
        )
    )


def downgrade() -> None:
    ml_model_versions = sa.table("ml_model_versions", sa.column("version", sa.String))

    op.execute(ml_model_versions.delete().where(ml_model_versions.c.version == "heuristic-v0"))

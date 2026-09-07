"""Initial schema — all five tables, ENUM types, indexes, and constraints.

Hand-authored from spec §18 (sections 18.2–18.6).

Revision ID: 0001
Revises: (none)
Create Date: 2026-09-07
"""

import sqlalchemy as sa
from geoalchemy2 import Geography
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

# Pre-define ENUM types with create_type=False since we CREATE TYPE explicitly
_facility_status = postgresql.ENUM(
    "OPEN", "CLOSED", "TEMPORARILY_UNAVAILABLE",
    name="facility_status",
    create_type=False,
)
_data_source = postgresql.ENUM(
    "REAL", "PUBLIC", "SYNTHETIC",
    name="data_source",
    create_type=False,
)


def upgrade() -> None:
    # ── ENUM types ───────────────────────────────────────────────────────
    op.execute(
        "CREATE TYPE facility_status AS ENUM "
        "('OPEN', 'CLOSED', 'TEMPORARILY_UNAVAILABLE')"
    )
    op.execute("CREATE TYPE data_source AS ENUM ('REAL', 'PUBLIC', 'SYNTHETIC')")

    # ── categories (spec §18.2) ──────────────────────────────────────────
    op.create_table(
        "categories",
        sa.Column(
            "id", sa.SmallInteger, primary_key=True, autoincrement=True
        ),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("label", sa.String(128), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_categories"),
        sa.UniqueConstraint("code", name="uq_categories_code"),
    )

    # ── facilities (spec §18.3) ──────────────────────────────────────────
    op.create_table(
        "facilities",
        sa.Column(
            "id", sa.BigInteger, primary_key=True, autoincrement=True
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category_id", sa.SmallInteger, nullable=False),
        sa.Column(
            "geom",
            Geography(
                geometry_type="POINT",
                srid=4326,
                spatial_index=False,
                from_text="ST_GeogFromText",
            ),
            nullable=False,
        ),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=False),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=False),
        sa.Column(
            "status",
            _facility_status,
            nullable=False,
            server_default=sa.text("'OPEN'"),
        ),
        sa.Column(
            "status_updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("rating", sa.Numeric(2, 1), nullable=True),
        sa.Column("capacity", sa.Integer, nullable=True),
        sa.Column("accessibility", sa.JSON, nullable=True),
        sa.Column("data_source", _data_source, nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_facilities"),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            name="fk_facilities_category_id_categories",
        ),
        sa.CheckConstraint(
            "rating BETWEEN 0 AND 5",
            name="rating_range",
        ),
        sa.CheckConstraint(
            "capacity > 0",
            name="capacity_positive",
        ),
    )

    op.create_index(
        "idx_facilities_geom",
        "facilities",
        ["geom"],
        postgresql_using="gist",
    )
    op.create_index(
        "idx_facilities_category", "facilities", ["category_id"]
    )
    op.create_index(
        "idx_facilities_open",
        "facilities",
        ["category_id"],
        postgresql_where=sa.text("status = 'OPEN' AND is_active"),
    )

    # ── usage_records (spec §18.4) ───────────────────────────────────────
    op.create_table(
        "usage_records",
        sa.Column(
            "id", sa.BigInteger, primary_key=True, autoincrement=True
        ),
        sa.Column("facility_id", sa.BigInteger, nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("hour", sa.SmallInteger, nullable=False),
        sa.Column("day_of_week", sa.SmallInteger, nullable=False),
        sa.Column(
            "usage_count",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "selection_count",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("data_source", _data_source, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_usage_records"),
        sa.ForeignKeyConstraint(
            ["facility_id"],
            ["facilities.id"],
            name="fk_usage_records_facility_id_facilities",
        ),
        sa.UniqueConstraint(
            "facility_id", "date", "hour", name="uq_usage_bucket"
        ),
        sa.CheckConstraint(
            "hour BETWEEN 0 AND 23",
            name="hour_range",
        ),
        sa.CheckConstraint(
            "day_of_week BETWEEN 0 AND 6",
            name="day_of_week_range",
        ),
    )

    op.create_index(
        "idx_usage_feature_lookup",
        "usage_records",
        ["facility_id", "day_of_week", "hour"],
    )

    # ── recommendation_logs (spec §18.5) ─────────────────────────────────
    op.create_table(
        "recommendation_logs",
        sa.Column(
            "id", sa.BigInteger, primary_key=True, autoincrement=True
        ),
        sa.Column("request_id", sa.Uuid, nullable=False),
        sa.Column("facility_id", sa.BigInteger, nullable=True),
        sa.Column("category_id", sa.SmallInteger, nullable=True),
        sa.Column("user_lat_rounded", sa.Numeric(5, 3), nullable=True),
        sa.Column("user_lon_rounded", sa.Numeric(6, 3), nullable=True),
        sa.Column("radius_m", sa.Integer, nullable=True),
        sa.Column("distance_m", sa.Numeric, nullable=True),
        sa.Column("predicted_usage", sa.Numeric, nullable=True),
        sa.Column("prediction_source", sa.String(16), nullable=True),
        sa.Column("recommendation_score", sa.Numeric, nullable=True),
        sa.Column("rank_position", sa.SmallInteger, nullable=True),
        sa.Column(
            "was_top_recommendation",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("model_version", sa.String(32), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_recommendation_logs"),
        sa.ForeignKeyConstraint(
            ["facility_id"],
            ["facilities.id"],
            name="fk_recommendation_logs_facility_id_facilities",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            name="fk_recommendation_logs_category_id_categories",
        ),
    )

    # ── ml_model_versions (spec §18.6) ───────────────────────────────────
    op.create_table(
        "ml_model_versions",
        sa.Column(
            "id", sa.Integer, primary_key=True, autoincrement=True
        ),
        sa.Column("version", sa.String(32), nullable=False),
        sa.Column("algorithm", sa.String(64), nullable=True),
        sa.Column(
            "trained_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column("feature_list", sa.JSON, nullable=True),
        sa.Column("evaluation_metrics", sa.JSON, nullable=True),
        sa.Column("artifact_path", sa.String(255), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("notes", sa.Text, nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_ml_model_versions"),
        sa.UniqueConstraint(
            "version", name="uq_ml_model_versions_version"
        ),
    )

    op.create_index(
        "uq_ml_model_versions_single_active",
        "ml_model_versions",
        ["is_active"],
        unique=True,
        postgresql_where=sa.text("is_active"),
    )


def downgrade() -> None:
    op.drop_table("ml_model_versions")
    op.drop_table("recommendation_logs")
    op.drop_table("usage_records")
    op.drop_table("facilities")
    op.drop_table("categories")
    op.execute("DROP TYPE data_source")
    op.execute("DROP TYPE facility_status")

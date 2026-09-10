"""drop pgrouting infrastructure

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-10 16:56:00.000000

"""

import geoalchemy2
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

from alembic import op

# revision identifiers, used by Alembic.
revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS campus_paths_vertices_pgr")
    op.drop_table("campus_paths")
    op.execute("DROP TYPE IF EXISTS path_type")


def downgrade() -> None:
    # Note: campus_paths_vertices_pgr is NOT recreated here.
    # It's a derived artifact of pgr_createTopology, not something a plain
    # migration can reconstruct.

    op.execute("CREATE TYPE path_type AS ENUM ('SIDEWALK','STAIRS','RAMP','CORRIDOR','CROSSING')")

    op.create_table(
        "campus_paths",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "geom",
            geoalchemy2.types.Geometry(
                geometry_type="LINESTRING", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"
            ),
            nullable=False,
        ),
        sa.Column(
            "path_type",
            ENUM(
                "SIDEWALK",
                "STAIRS",
                "RAMP",
                "CORRIDOR",
                "CROSSING",
                name="path_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("cost", sa.Double(), nullable=False),
        sa.Column("reverse_cost", sa.Double(), nullable=False),
        sa.Column("source", sa.BigInteger(), nullable=True),
        sa.Column("target", sa.BigInteger(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "data_source",
            ENUM("REAL", "PUBLIC", "SYNTHETIC", name="data_source", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("idx_campus_paths_source", "campus_paths", ["source"], unique=False)
    op.create_index("idx_campus_paths_target", "campus_paths", ["target"], unique=False)

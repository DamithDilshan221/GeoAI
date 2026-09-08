"""add campus_paths table

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-08 10:17:00.000000

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the path_type ENUM
    op.execute("CREATE TYPE path_type AS ENUM ('SIDEWALK','STAIRS','RAMP','CORRIDOR','CROSSING')")

    from sqlalchemy.dialects.postgresql import ENUM

    # Create the campus_paths table
    op.create_table(
        'campus_paths',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('geom', geoalchemy2.types.Geometry(geometry_type='LINESTRING', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
        sa.Column('path_type', ENUM('SIDEWALK', 'STAIRS', 'RAMP', 'CORRIDOR', 'CROSSING', name='path_type', create_type=False), nullable=False),
        sa.Column('cost', sa.Double(), nullable=False),
        sa.Column('reverse_cost', sa.Double(), nullable=False),
        sa.Column('source', sa.BigInteger(), nullable=True),
        sa.Column('target', sa.BigInteger(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('data_source', ENUM('REAL', 'PUBLIC', 'SYNTHETIC', name='data_source', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indices
    op.create_index('idx_campus_paths_source', 'campus_paths', ['source'], unique=False)
    op.create_index('idx_campus_paths_target', 'campus_paths', ['target'], unique=False)


def downgrade() -> None:
    # Drop indices
    op.drop_index('idx_campus_paths_target', table_name='campus_paths')
    op.drop_index('idx_campus_paths_source', table_name='campus_paths')

    # Drop table
    op.drop_table('campus_paths')

    # Drop the ENUM type
    op.execute("DROP TYPE path_type")

"""v3 washroom schema

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-10 16:55:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE TYPE audience_type AS ENUM ('VISITOR', 'STAFF')")
    op.add_column('facilities', sa.Column(
        'audience',
        postgresql.ENUM('VISITOR', 'STAFF', name='audience_type', create_type=False),
        nullable=False, server_default='VISITOR',
    ))
    op.add_column('facilities', sa.Column('location_name', sa.String(200), nullable=True))
    op.add_column('facilities', sa.Column(
        'fixtures', postgresql.JSONB(astext_type=sa.Text()),
        nullable=False, server_default=sa.text("'{}'::jsonb"),
    ))
    op.execute("""
        ALTER TABLE facilities ADD COLUMN total_stalls INTEGER
        GENERATED ALWAYS AS (
            COALESCE((fixtures->>'attached')::INT, 0)
            + COALESCE((fixtures->>'normal')::INT, 0)
        ) STORED
    """)
    op.create_index('idx_facilities_audience', 'facilities', ['audience'])
    op.drop_column('facilities', 'capacity')
    op.drop_column('facilities', 'accessibility')


def downgrade() -> None:
    op.add_column('facilities', sa.Column(
        'accessibility', postgresql.JSONB(astext_type=sa.Text()), nullable=True,
    ))
    op.add_column('facilities', sa.Column(
        'capacity', sa.Integer(), sa.CheckConstraint('capacity > 0', name='ck_facilities_capacity'),
        nullable=True,
    ))
    op.drop_index('idx_facilities_audience', table_name='facilities')
    op.drop_column('facilities', 'total_stalls')
    op.drop_column('facilities', 'fixtures')
    op.drop_column('facilities', 'location_name')
    op.drop_column('facilities', 'audience')
    op.execute("DROP TYPE audience_type")

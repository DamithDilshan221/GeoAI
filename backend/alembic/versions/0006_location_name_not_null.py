"""location_name not null

Revision ID: 0006
Revises: 0005
Create Date: 2026-09-10 17:20:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE facilities SET location_name = name WHERE location_name IS NULL")
    op.alter_column("facilities", "location_name", nullable=False)


def downgrade() -> None:
    op.alter_column("facilities", "location_name", nullable=True)

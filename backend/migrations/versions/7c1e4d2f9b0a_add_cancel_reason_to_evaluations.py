"""add cancel_reason to evaluations

Revision ID: 7c1e4d2f9b0a
Revises: 4a2b8c9d5e6f
Create Date: 2025-12-14 20:48:00
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7c1e4d2f9b0a"
down_revision = "4a2b8c9d5e6f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("evaluations", sa.Column("cancel_reason", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("evaluations", "cancel_reason")

"""merge heads cancel_reason and client_id

Revision ID: 8f3b2c1d4e5a
Revises: 7c1e4d2f9b0a, d9c3f0f12345
Create Date: 2025-12-14 21:55:00
"""

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

# revision identifiers, used by Alembic.
revision = "8f3b2c1d4e5a"
down_revision = ("7c1e4d2f9b0a", "d9c3f0f12345")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

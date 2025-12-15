"""add process fields to evaluations

Revision ID: 3e2f7b8a9cde
Revises: 8f3b2c1d4e5a
Create Date: 2025-12-15 00:00:00
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3e2f7b8a9cde"
down_revision = "8f3b2c1d4e5a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("evaluations", sa.Column("test_process", sa.Text(), nullable=True))
    op.add_column("evaluations", sa.Column("v_process", sa.Text(), nullable=True))
    op.add_column("evaluations", sa.Column("pgm_login_text", sa.Text(), nullable=True))
    op.add_column("evaluations", sa.Column("pgm_login_image", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("evaluations", "pgm_login_image")
    op.drop_column("evaluations", "pgm_login_text")
    op.drop_column("evaluations", "v_process")
    op.drop_column("evaluations", "test_process")

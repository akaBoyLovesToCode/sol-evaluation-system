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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "evaluations" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("evaluations")}
    if "test_process" not in existing_columns:
        op.add_column("evaluations", sa.Column("test_process", sa.Text(), nullable=True))
    if "v_process" not in existing_columns:
        op.add_column("evaluations", sa.Column("v_process", sa.Text(), nullable=True))
    if "pgm_login_text" not in existing_columns:
        op.add_column("evaluations", sa.Column("pgm_login_text", sa.Text(), nullable=True))
    if "pgm_login_image" not in existing_columns:
        op.add_column("evaluations", sa.Column("pgm_login_image", sa.Text(), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "evaluations" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("evaluations")}
    if "pgm_login_image" in existing_columns:
        op.drop_column("evaluations", "pgm_login_image")
    if "pgm_login_text" in existing_columns:
        op.drop_column("evaluations", "pgm_login_text")
    if "v_process" in existing_columns:
        op.drop_column("evaluations", "v_process")
    if "test_process" in existing_columns:
        op.drop_column("evaluations", "test_process")

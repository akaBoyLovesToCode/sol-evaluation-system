"""add evaluation_name to evaluations

Revision ID: c8d9e0f1a2b3
Revises: b7c6d5e4f3a2
Create Date: 2026-06-24 10:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "c8d9e0f1a2b3"
down_revision = "b7c6d5e4f3a2"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "evaluations" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"] for column in inspector.get_columns("evaluations")
    }
    if "evaluation_name" not in existing_columns:
        with op.batch_alter_table("evaluations", schema=None) as batch_op:
            batch_op.add_column(
                sa.Column("evaluation_name", sa.String(length=255), nullable=True)
            )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "evaluations" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"] for column in inspector.get_columns("evaluations")
    }
    if "evaluation_name" in existing_columns:
        with op.batch_alter_table("evaluations", schema=None) as batch_op:
            batch_op.drop_column("evaluation_name")

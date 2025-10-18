"""add_title_to_evaluation_processes

Revision ID: 1b2a3c4d5e6f
Revises: ee9a7b3f3b9a
Create Date: 2025-09-17 20:25:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1b2a3c4d5e6f"
down_revision = "ee9a7b3f3b9a"
branch_labels = None
depends_on = None


def upgrade():
    # Add the missing 'title' column to evaluation_processes
    with op.batch_alter_table("evaluation_processes", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("title", sa.String(length=100), nullable=False, server_default="")
        )

    # Optionally drop the server default after backfilling existing rows
    with op.batch_alter_table("evaluation_processes", schema=None) as batch_op:
        batch_op.alter_column("title", server_default=None)


def downgrade():
    with op.batch_alter_table("evaluation_processes", schema=None) as batch_op:
        batch_op.drop_column("title")

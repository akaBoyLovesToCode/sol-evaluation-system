"""add pgm_test_time to evaluations

Revision ID: f1a2b3c4d5e6
Revises: 3e2f7b8a9cde
Create Date: 2026-03-23 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f1a2b3c4d5e6"
down_revision = "3e2f7b8a9cde"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "evaluations" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("evaluations")}
    if "pgm_test_time" not in existing_columns:
        with op.batch_alter_table("evaluations", schema=None) as batch_op:
            batch_op.add_column(sa.Column("pgm_test_time", sa.String(length=100), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "evaluations" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("evaluations")}
    if "pgm_test_time" in existing_columns:
        with op.batch_alter_table("evaluations", schema=None) as batch_op:
            batch_op.drop_column("pgm_test_time")

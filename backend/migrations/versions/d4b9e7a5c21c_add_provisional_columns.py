"""add provisional flags to fail codes

Revision ID: d4b9e7a5c21c
Revises: c3c5c2dea1d5
Create Date: 2025-01-11 21:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d4b9e7a5c21c"
down_revision = "c3c5c2dea1d5"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "fail_codes" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("fail_codes")}

    if "is_provisional" not in existing_columns:
        op.add_column(
            "fail_codes",
            sa.Column(
                "is_provisional",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("0"),
            ),
        )
        op.alter_column(
            "fail_codes",
            "is_provisional",
            existing_type=sa.Boolean(),
            server_default=None,
        )

    if "source" not in existing_columns:
        op.add_column(
            "fail_codes", sa.Column("source", sa.String(length=64), nullable=True)
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "fail_codes" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("fail_codes")}
    if "source" in existing_columns:
        op.drop_column("fail_codes", "source")
    if "is_provisional" in existing_columns:
        op.drop_column("fail_codes", "is_provisional")

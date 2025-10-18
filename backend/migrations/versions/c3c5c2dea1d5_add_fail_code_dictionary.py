"""add fail code dictionary

Revision ID: c3c5c2dea1d5
Revises: 4a2b8c9d5e6f
Create Date: 2025-01-11 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c3c5c2dea1d5"
down_revision = "1b2a3c4d5e6f"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    table_names = inspector.get_table_names()
    if "fail_codes" not in table_names:
        op.create_table(
            "fail_codes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("code", sa.String(length=32), nullable=False),
            sa.Column("short_name", sa.String(length=255), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column(
                "is_provisional",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("0"),
            ),
            sa.Column("source", sa.String(length=64), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("code"),
        )
        op.alter_column(
            "fail_codes",
            "is_provisional",
            existing_type=sa.Boolean(),
            server_default=None,
        )
    else:
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

    existing_indexes = {idx.get("name") for idx in inspector.get_indexes("fail_codes")}
    target_index = op.f("ix_fail_codes_code")
    if target_index not in existing_indexes:
        op.create_index(target_index, "fail_codes", ["code"], unique=False)


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    target_index = op.f("ix_fail_codes_code")
    if "fail_codes" in inspector.get_table_names():
        existing_indexes = {
            idx.get("name") for idx in inspector.get_indexes("fail_codes")
        }
        if target_index in existing_indexes:
            op.drop_index(target_index, table_name="fail_codes")
        op.drop_table("fail_codes")

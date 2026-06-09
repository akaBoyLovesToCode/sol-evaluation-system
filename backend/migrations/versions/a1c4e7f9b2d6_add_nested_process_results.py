"""add nested process results

Revision ID: a1c4e7f9b2d6
Revises: f1a2b3c4d5e6
Create Date: 2026-06-09 20:45:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "a1c4e7f9b2d6"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "evaluation_nested_processes"

    if table_name not in inspector.get_table_names():
        op.create_table(
            table_name,
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("evaluation_id", sa.Integer(), nullable=False),
            sa.Column("process_key", sa.String(length=64), nullable=False),
            sa.Column("process_name", sa.String(length=255), nullable=False),
            sa.Column("order_index", sa.Integer(), nullable=False),
            sa.Column("result_html", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["evaluation_id"], ["evaluations.id"], ondelete="CASCADE"
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "evaluation_id",
                "process_key",
                name="uq_evaluation_nested_process_key",
            ),
        )

    inspector = sa.inspect(bind)
    existing_indexes = {index["name"] for index in inspector.get_indexes(table_name)}
    index_name = op.f("ix_evaluation_nested_processes_evaluation_id")
    if index_name not in existing_indexes:
        op.create_index(
            index_name,
            table_name,
            ["evaluation_id"],
            unique=False,
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "evaluation_nested_processes"
    if table_name not in inspector.get_table_names():
        return

    existing_indexes = {index["name"] for index in inspector.get_indexes(table_name)}
    index_name = op.f("ix_evaluation_nested_processes_evaluation_id")
    if index_name in existing_indexes:
        op.drop_index(index_name, table_name=table_name)
    op.drop_table(table_name)

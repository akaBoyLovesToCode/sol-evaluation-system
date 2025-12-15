"""add client id to nested lots

Revision ID: d9c3f0f12345
Revises: cb5f5c9371b1
Create Date: 2025-09-05 13:20:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d9c3f0f12345"
down_revision = "cb5f5c9371b1"
branch_labels = None
depends_on = None


def _existing_columns(inspector, table_name):
    return {col["name"] for col in inspector.get_columns(table_name)}


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    index_name = op.f("ix_evaluation_process_lots_eval_proc_client")

    if "evaluation_process_lots" in inspector.get_table_names():
        existing = _existing_columns(inspector, "evaluation_process_lots")
        with op.batch_alter_table("evaluation_process_lots") as batch:
            if "client_id" not in existing:
                batch.add_column(
                    sa.Column("client_id", sa.String(length=64), nullable=True)
                )
        existing_indexes = {
            idx["name"] for idx in inspector.get_indexes("evaluation_process_lots")
        }
        if index_name not in existing_indexes:
            op.create_index(
                index_name,
                "evaluation_process_lots",
                ["evaluation_id", "process_key", "client_id"],
                unique=False,
            )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    index_name = op.f("ix_evaluation_process_lots_eval_proc_client")

    if "evaluation_process_lots" in inspector.get_table_names():
        existing_indexes = {
            idx["name"] for idx in inspector.get_indexes("evaluation_process_lots")
        }
        if index_name in existing_indexes:
            op.drop_index(index_name, table_name="evaluation_process_lots")
        existing = _existing_columns(inspector, "evaluation_process_lots")
        with op.batch_alter_table("evaluation_process_lots") as batch:
            if "client_id" in existing:
                batch.drop_column("client_id")

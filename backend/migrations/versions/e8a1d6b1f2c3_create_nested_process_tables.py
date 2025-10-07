"""create nested process tables

Revision ID: e8a1d6b1f2c3
Revises: d4b9e7a5c21c
Create Date: 2025-01-11 22:15:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e8a1d6b1f2c3"
down_revision = "d4b9e7a5c21c"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # evaluation_processes_raw
    if "evaluation_processes_raw" not in inspector.get_table_names():
        op.create_table(
            "evaluation_processes_raw",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("evaluation_id", sa.Integer(), nullable=False),
            sa.Column("payload", sa.JSON(), nullable=False),
            sa.Column("source", sa.String(length=32), nullable=False, server_default="rc0"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["evaluation_id"], ["evaluations.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_evaluation_processes_raw_evaluation_id"),
            "evaluation_processes_raw",
            ["evaluation_id"],
            unique=False,
        )
        op.alter_column(
            "evaluation_processes_raw",
            "source",
            existing_type=sa.String(length=32),
            server_default=None,
        )
    else:
        existing_columns = {
            col["name"] for col in inspector.get_columns("evaluation_processes_raw")
        }
        if "source" not in existing_columns:
            op.add_column(
                "evaluation_processes_raw",
                sa.Column("source", sa.String(length=32), nullable=True),
            )
        existing_indexes = {
            idx["name"] for idx in inspector.get_indexes("evaluation_processes_raw")
        }
        if op.f("ix_evaluation_processes_raw_evaluation_id") not in existing_indexes:
            op.create_index(
                op.f("ix_evaluation_processes_raw_evaluation_id"),
                "evaluation_processes_raw",
                ["evaluation_id"],
                unique=False,
            )

    # evaluation_process_steps
    if "evaluation_process_steps" not in inspector.get_table_names():
        op.create_table(
            "evaluation_process_steps",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("evaluation_id", sa.Integer(), nullable=False),
            sa.Column("lot_number", sa.String(length=100), nullable=False),
            sa.Column("quantity", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("order_index", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("step_code", sa.String(length=32), nullable=False),
            sa.Column("step_label", sa.String(length=255), nullable=True),
            sa.Column("eval_code", sa.String(length=64), nullable=False),
            sa.Column("total_units", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("pass_units", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("fail_units", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["evaluation_id"], ["evaluations.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_evaluation_process_steps_evaluation_id"),
            "evaluation_process_steps",
            ["evaluation_id"],
            unique=False,
        )
    else:
        existing_indexes = {
            idx["name"] for idx in inspector.get_indexes("evaluation_process_steps")
        }
        if op.f("ix_evaluation_process_steps_evaluation_id") not in existing_indexes:
            op.create_index(
                op.f("ix_evaluation_process_steps_evaluation_id"),
                "evaluation_process_steps",
                ["evaluation_id"],
                unique=False,
            )

    # evaluation_step_failures
    if "evaluation_step_failures" not in inspector.get_table_names():
        op.create_table(
            "evaluation_step_failures",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("step_id", sa.Integer(), nullable=False),
            sa.Column("sequence", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("serial_number", sa.String(length=100), nullable=True),
            sa.Column("fail_code_id", sa.Integer(), nullable=True),
            sa.Column("fail_code_text", sa.String(length=32), nullable=False),
            sa.Column("fail_code_name_snapshot", sa.String(length=255), nullable=True),
            sa.Column("analysis_result", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["fail_code_id"], ["fail_codes.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["step_id"], ["evaluation_process_steps.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_evaluation_step_failures_step_id"),
            "evaluation_step_failures",
            ["step_id"],
            unique=False,
        )
    else:
        existing_indexes = {
            idx["name"] for idx in inspector.get_indexes("evaluation_step_failures")
        }
        if op.f("ix_evaluation_step_failures_step_id") not in existing_indexes:
            op.create_index(
                op.f("ix_evaluation_step_failures_step_id"),
                "evaluation_step_failures",
                ["step_id"],
                unique=False,
            )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "evaluation_step_failures" in inspector.get_table_names():
        existing_indexes = {
            idx["name"] for idx in inspector.get_indexes("evaluation_step_failures")
        }
        if op.f("ix_evaluation_step_failures_step_id") in existing_indexes:
            op.drop_index(
                op.f("ix_evaluation_step_failures_step_id"),
                table_name="evaluation_step_failures",
            )
        op.drop_table("evaluation_step_failures")

    if "evaluation_process_steps" in inspector.get_table_names():
        existing_indexes = {
            idx["name"] for idx in inspector.get_indexes("evaluation_process_steps")
        }
        if op.f("ix_evaluation_process_steps_evaluation_id") in existing_indexes:
            op.drop_index(
                op.f("ix_evaluation_process_steps_evaluation_id"),
                table_name="evaluation_process_steps",
            )
        op.drop_table("evaluation_process_steps")

    if "evaluation_processes_raw" in inspector.get_table_names():
        existing_indexes = {
            idx["name"] for idx in inspector.get_indexes("evaluation_processes_raw")
        }
        if op.f("ix_evaluation_processes_raw_evaluation_id") in existing_indexes:
            op.drop_index(
                op.f("ix_evaluation_processes_raw_evaluation_id"),
                table_name="evaluation_processes_raw",
            )
        op.drop_table("evaluation_processes_raw")

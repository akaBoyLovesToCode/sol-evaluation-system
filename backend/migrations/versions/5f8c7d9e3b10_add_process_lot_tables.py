"""add process lot tables

Revision ID: 5f8c7d9e3b10
Revises: 4a2b8c9d5e6f
Create Date: 2025-09-02 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5f8c7d9e3b10"
down_revision = "e8a1d6b1f2c3"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    table_names = set(inspector.get_table_names())

    if "evaluation_process_lots" not in table_names:
        op.create_table(
            "evaluation_process_lots",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("evaluation_id", sa.Integer(), nullable=False),
            sa.Column("lot_number", sa.String(length=100), nullable=False),
            sa.Column("quantity", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(
                ["evaluation_id"],
                ["evaluations.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_evaluation_process_lots_evaluation_id"),
            "evaluation_process_lots",
            ["evaluation_id"],
            unique=False,
        )
        op.alter_column(
            "evaluation_process_lots",
            "quantity",
            existing_type=sa.Integer(),
            server_default=None,
        )
    else:
        existing_indexes = {
            idx["name"] for idx in inspector.get_indexes("evaluation_process_lots")
        }
        if op.f("ix_evaluation_process_lots_evaluation_id") not in existing_indexes:
            op.create_index(
                op.f("ix_evaluation_process_lots_evaluation_id"),
                "evaluation_process_lots",
                ["evaluation_id"],
                unique=False,
            )

    if "evaluation_step_lots" not in table_names:
        op.create_table(
            "evaluation_step_lots",
            sa.Column("step_id", sa.Integer(), nullable=False),
            sa.Column("lot_id", sa.Integer(), nullable=False),
            sa.Column("quantity_override", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(
                ["lot_id"],
                ["evaluation_process_lots.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["step_id"],
                ["evaluation_process_steps.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("step_id", "lot_id"),
        )
        op.create_index(
            op.f("ix_evaluation_step_lots_step_id"),
            "evaluation_step_lots",
            ["step_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_evaluation_step_lots_lot_id"),
            "evaluation_step_lots",
            ["lot_id"],
            unique=False,
        )
    else:
        existing_indexes = {
            idx["name"] for idx in inspector.get_indexes("evaluation_step_lots")
        }
        if op.f("ix_evaluation_step_lots_step_id") not in existing_indexes:
            op.create_index(
                op.f("ix_evaluation_step_lots_step_id"),
                "evaluation_step_lots",
                ["step_id"],
                unique=False,
            )
        if op.f("ix_evaluation_step_lots_lot_id") not in existing_indexes:
            op.create_index(
                op.f("ix_evaluation_step_lots_lot_id"),
                "evaluation_step_lots",
                ["lot_id"],
                unique=False,
            )

    if "evaluation_process_steps" in table_names:
        step_columns = {
            column["name"]: column
            for column in inspector.get_columns("evaluation_process_steps")
        }
        if "results_applicable" not in step_columns:
            op.add_column(
                "evaluation_process_steps",
                sa.Column(
                    "results_applicable",
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.true(),
                ),
            )
            op.execute(
                "UPDATE evaluation_process_steps SET results_applicable = 1 WHERE results_applicable IS NULL"
            )
            op.alter_column(
                "evaluation_process_steps", "results_applicable", server_default=None
            )
        if "total_units_manual" not in step_columns:
            op.add_column(
                "evaluation_process_steps",
                sa.Column(
                    "total_units_manual",
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.false(),
                ),
            )
            op.execute(
                "UPDATE evaluation_process_steps SET total_units_manual = 0 WHERE total_units_manual IS NULL"
            )
            op.alter_column(
                "evaluation_process_steps", "total_units_manual", server_default=None
            )

        op.alter_column(
            "evaluation_process_steps",
            "eval_code",
            existing_type=sa.String(length=64),
            existing_nullable=False,
            nullable=True,
        )
        op.alter_column(
            "evaluation_process_steps",
            "total_units",
            existing_type=sa.Integer(),
            existing_nullable=False,
            nullable=True,
            server_default=None,
        )
        op.alter_column(
            "evaluation_process_steps",
            "pass_units",
            existing_type=sa.Integer(),
            existing_nullable=False,
            nullable=True,
            server_default=None,
        )
        op.alter_column(
            "evaluation_process_steps",
            "fail_units",
            existing_type=sa.Integer(),
            existing_nullable=False,
            nullable=True,
            server_default=None,
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    table_names = set(inspector.get_table_names())

    if "evaluation_step_lots" in table_names:
        op.drop_table("evaluation_step_lots")

    if "evaluation_process_lots" in table_names:
        op.drop_table("evaluation_process_lots")

    if "evaluation_process_steps" in table_names:
        op.execute(
            "UPDATE evaluation_process_steps SET eval_code = '' WHERE eval_code IS NULL"
        )
        op.execute(
            "UPDATE evaluation_process_steps SET total_units = 0 WHERE total_units IS NULL"
        )
        op.execute(
            "UPDATE evaluation_process_steps SET pass_units = 0 WHERE pass_units IS NULL"
        )
        op.execute(
            "UPDATE evaluation_process_steps SET fail_units = 0 WHERE fail_units IS NULL"
        )
        op.alter_column(
            "evaluation_process_steps",
            "eval_code",
            existing_type=sa.String(length=64),
            existing_nullable=True,
            nullable=False,
        )
        op.alter_column(
            "evaluation_process_steps",
            "total_units",
            existing_type=sa.Integer(),
            existing_nullable=True,
            nullable=False,
            server_default="0",
        )
        op.alter_column(
            "evaluation_process_steps",
            "pass_units",
            existing_type=sa.Integer(),
            existing_nullable=True,
            nullable=False,
            server_default="0",
        )
        op.alter_column(
            "evaluation_process_steps",
            "fail_units",
            existing_type=sa.Integer(),
            existing_nullable=True,
            nullable=False,
            server_default="0",
        )
        step_columns = {
            column["name"]: column
            for column in inspector.get_columns("evaluation_process_steps")
        }
        if "total_units_manual" in step_columns:
            op.drop_column("evaluation_process_steps", "total_units_manual")
        if "results_applicable" in step_columns:
            op.drop_column("evaluation_process_steps", "results_applicable")

"""simplify_remove_auth_users_and_ip_logging

Revision ID: ee9a7b3f3b9a
Revises: d861685a6b7f
Create Date: 2025-09-15 22:45:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ee9a7b3f3b9a"
down_revision = "d861685a6b7f"
branch_labels = None
depends_on = None


def _table_exists(inspector, table_name: str) -> bool:
    try:
        return table_name in inspector.get_table_names()
    except Exception:
        return False


def _columns(inspector, table_name: str) -> set[str]:
    try:
        return {col["name"] for col in inspector.get_columns(table_name)}
    except Exception:
        return set()


def _drop_user_foreign_keys(inspector, table_name: str) -> None:
    try:
        fks = inspector.get_foreign_keys(table_name)
    except Exception:
        fks = []
    for fk in fks:
        if fk.get("referred_table") == "users":
            name = fk.get("name")
            if name:
                op.drop_constraint(name, table_name, type_="foreignkey")


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1) evaluations: drop user-based FKs/columns; add charger name fields
    if _table_exists(inspector, "evaluations"):
        _drop_user_foreign_keys(inspector, "evaluations")
        cols = _columns(inspector, "evaluations")

        # Drop old user reference columns if present
        for col in (
            "evaluator_id",
            "part_approver_id",
            "group_approver_id",
            "scs_charger_id",
            "head_office_charger_id",
        ):
            if col in cols:
                op.drop_column("evaluations", col)

        # Add new free-text charger fields
        cols = _columns(inspector, "evaluations")  # refresh
        if "scs_charger_name" not in cols:
            op.add_column(
                "evaluations",
                sa.Column("scs_charger_name", sa.String(length=100), nullable=True),
            )
        if "head_office_charger_name" not in cols:
            op.add_column(
                "evaluations",
                sa.Column(
                    "head_office_charger_name", sa.String(length=100), nullable=True
                ),
            )

    # 2) operation_logs: drop user_id FK/column; add request metadata fields
    if _table_exists(inspector, "operation_logs"):
        _drop_user_foreign_keys(inspector, "operation_logs")
        cols = _columns(inspector, "operation_logs")

        if "user_id" in cols:
            op.drop_column("operation_logs", "user_id")

        # Add request metadata if not present
        cols = _columns(inspector, "operation_logs")  # refresh
        if "request_method" not in cols:
            op.add_column(
                "operation_logs",
                sa.Column("request_method", sa.String(length=10), nullable=True),
            )
        if "request_path" not in cols:
            op.add_column(
                "operation_logs",
                sa.Column("request_path", sa.String(length=200), nullable=True),
            )
        if "query_string" not in cols:
            op.add_column(
                "operation_logs", sa.Column("query_string", sa.Text(), nullable=True)
            )
        if "status_code" not in cols:
            op.add_column(
                "operation_logs", sa.Column("status_code", sa.Integer(), nullable=True)
            )

    # 3) Drop obsolete tables (users, messages) if present
    for tbl in ("messages", "users"):
        if _table_exists(inspector, tbl):
            op.drop_table(tbl)


def downgrade() -> None:
    # Best-effort partial downgrade: reverse added columns.
    # Note: user tables/relationships are not fully restored.
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _table_exists(inspector, "evaluations"):
        cols = _columns(inspector, "evaluations")
        if "scs_charger_name" in cols:
            op.drop_column("evaluations", "scs_charger_name")
        if "head_office_charger_name" in cols:
            op.drop_column("evaluations", "head_office_charger_name")
        # Recreate integer columns without FKs to allow manual restoration if needed
        cols = _columns(inspector, "evaluations")
        for col, typ in (
            ("evaluator_id", sa.Integer()),
            ("part_approver_id", sa.Integer()),
            ("group_approver_id", sa.Integer()),
            ("scs_charger_id", sa.Integer()),
            ("head_office_charger_id", sa.Integer()),
        ):
            if col not in cols:
                op.add_column("evaluations", sa.Column(col, typ, nullable=True))

    if _table_exists(inspector, "operation_logs"):
        cols = _columns(inspector, "operation_logs")
        for col in ("request_method", "request_path", "query_string", "status_code"):
            if col in cols:
                op.drop_column("operation_logs", col)
        if "user_id" not in _columns(inspector, "operation_logs"):
            op.add_column(
                "operation_logs", sa.Column("user_id", sa.Integer(), nullable=True)
            )
    # Users/messages tables are not recreated in downgrade.
    # If full downgrade is required, reintroduce the dropped models and constraints.

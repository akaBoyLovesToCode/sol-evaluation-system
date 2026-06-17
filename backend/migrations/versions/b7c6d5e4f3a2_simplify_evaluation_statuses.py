"""simplify evaluation statuses

Revision ID: b7c6d5e4f3a2
Revises: a1c4e7f9b2d6
Create Date: 2026-06-17 10:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "b7c6d5e4f3a2"
down_revision = "a1c4e7f9b2d6"
branch_labels = None
depends_on = None

OLD_STATUSES = (
    "draft",
    "in_progress",
    "pending_part_approval",
    "pending_group_approval",
    "completed",
    "paused",
    "cancelled",
    "rejected",
)
NEW_STATUSES = ("in_progress", "completed", "cancelled")


def _status_enum(values):
    return sa.Enum(*values, name="evaluation_status")


def _alter_status_enum(values, existing_values, server_default=None):
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "evaluations" not in inspector.get_table_names():
        return

    kwargs = {
        "existing_type": _status_enum(existing_values),
        "type_": _status_enum(values),
        "existing_nullable": False,
    }
    if server_default is not None:
        kwargs["server_default"] = server_default

    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("evaluations", schema=None) as batch_op:
            batch_op.alter_column("status", **kwargs)
        return

    op.alter_column("evaluations", "status", **kwargs)


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "evaluations" not in inspector.get_table_names():
        return

    op.execute("UPDATE evaluations SET status = 'cancelled' WHERE status = 'rejected'")
    op.execute(
        "UPDATE evaluations SET status = 'in_progress' "
        "WHERE status IN ('draft', 'pending_part_approval', "
        "'pending_group_approval', 'paused')"
    )
    _alter_status_enum(NEW_STATUSES, OLD_STATUSES, server_default="in_progress")


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "evaluations" not in inspector.get_table_names():
        return

    _alter_status_enum(OLD_STATUSES, NEW_STATUSES, server_default="draft")

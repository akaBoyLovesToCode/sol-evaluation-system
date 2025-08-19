"""Add comments and mentions tables for evaluation discussions

Revision ID: 4a2b8c9d5e6f
Revises: 3138e7668b9f
Create Date: 2024-01-15 10:30:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4a2b8c9d5e6f"
down_revision = "3138e7668b9f"
branch_labels = None
depends_on = None


def upgrade():
    # Create comments table
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evaluation_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("parent_comment_id", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_edited", sa.Boolean(), nullable=False, default=False),
        sa.Column("edited_at", sa.DateTime(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, default=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["evaluation_id"], ["evaluations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["parent_comment_id"], ["comments.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for comments
    op.create_index("idx_comments_evaluation_id", "comments", ["evaluation_id"])
    op.create_index("idx_comments_user_id", "comments", ["user_id"])
    op.create_index("idx_comments_parent_id", "comments", ["parent_comment_id"])
    op.create_index("idx_comments_created_at", "comments", ["created_at"])

    # Create mentions table
    op.create_table(
        "mentions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "mention_type",
            sa.Enum(
                "evaluation_comment",
                "evaluation_description",
                "message",
                "task_assignment",
                name="mention_types",
            ),
            nullable=False,
        ),
        sa.Column("mentioned_user_id", sa.Integer(), nullable=False),
        sa.Column("mentioner_id", sa.Integer(), nullable=False),
        sa.Column("evaluation_id", sa.Integer(), nullable=True),
        sa.Column("message_id", sa.Integer(), nullable=True),
        sa.Column("comment_id", sa.Integer(), nullable=True),
        sa.Column("context_text", sa.Text(), nullable=True),
        sa.Column("mention_position", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("unread", "read", "acknowledged", name="mention_status"),
            nullable=False,
            default="unread",
        ),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["mentioned_user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["mentioner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["evaluation_id"], ["evaluations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["comment_id"], ["comments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for mentions
    op.create_index("idx_mentions_mentioned_user", "mentions", ["mentioned_user_id"])
    op.create_index("idx_mentions_mentioner", "mentions", ["mentioner_id"])
    op.create_index("idx_mentions_evaluation", "mentions", ["evaluation_id"])
    op.create_index("idx_mentions_status", "mentions", ["status"])
    op.create_index("idx_mentions_created_at", "mentions", ["created_at"])
    op.create_index(
        "idx_mentions_user_status",
        "mentions",
        ["mentioned_user_id", "status"],
    )

    # Add comment_id foreign key to messages table for comment notifications
    with op.batch_alter_table("messages", schema=None) as batch_op:
        batch_op.add_column(sa.Column("comment_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_messages_comment_id",
            "comments",
            ["comment_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade():
    # Remove comment_id from messages table
    with op.batch_alter_table("messages", schema=None) as batch_op:
        batch_op.drop_constraint("fk_messages_comment_id", type_="foreignkey")
        batch_op.drop_column("comment_id")

    # Drop indexes for mentions
    op.drop_index("idx_mentions_user_status", table_name="mentions")
    op.drop_index("idx_mentions_created_at", table_name="mentions")
    op.drop_index("idx_mentions_status", table_name="mentions")
    op.drop_index("idx_mentions_evaluation", table_name="mentions")
    op.drop_index("idx_mentions_mentioner", table_name="mentions")
    op.drop_index("idx_mentions_mentioned_user", table_name="mentions")

    # Drop mentions table
    op.drop_table("mentions")

    # Drop enum types for mentions
    sa.Enum(name="mention_types").drop(op.get_bind(), checkfirst=False)
    sa.Enum(name="mention_status").drop(op.get_bind(), checkfirst=False)

    # Drop indexes for comments
    op.drop_index("idx_comments_created_at", table_name="comments")
    op.drop_index("idx_comments_parent_id", table_name="comments")
    op.drop_index("idx_comments_user_id", table_name="comments")
    op.drop_index("idx_comments_evaluation_id", table_name="comments")

    # Drop comments table
    op.drop_table("comments")

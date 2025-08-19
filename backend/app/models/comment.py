"""Comment model for evaluation discussions in Solution Evaluation System

This model handles comments on evaluations, supporting nested replies,
mentions, and soft deletion.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from app import db

if TYPE_CHECKING:
    pass


class Comment(db.Model):
    """Model for comments on evaluations

    Supports:
    - Nested comments (replies)
    - Mentions of users
    - Soft deletion
    - Edit tracking
    """

    __tablename__ = "comments"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign keys
    evaluation_id = db.Column(
        db.Integer, db.ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    parent_comment_id = db.Column(
        db.Integer, db.ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )

    # Comment content
    content = db.Column(db.Text, nullable=False)

    # Edit tracking
    is_edited = db.Column(db.Boolean, default=False, nullable=False)
    edited_at = db.Column(db.DateTime, nullable=True)

    # Soft deletion
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    evaluation = db.relationship(
        "Evaluation", backref=db.backref("comments", lazy="dynamic")
    )
    user = db.relationship("User", backref=db.backref("user_comments", lazy="dynamic"))
    parent = db.relationship(
        "Comment",
        remote_side=[id],
        backref=db.backref("replies", lazy="dynamic", cascade="all, delete-orphan"),
    )
    mentions = db.relationship(
        "Mention",
        primaryjoin="and_(Mention.comment_id==Comment.id)",
        foreign_keys="[Mention.comment_id]",
        lazy="dynamic",
        cascade="all, delete-orphan",
        overlaps="comment,comment_mentions",
    )

    def __init__(
        self,
        evaluation_id: int,
        user_id: int,
        content: str,
        parent_comment_id: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize comment with required fields

        Args:
            evaluation_id: ID of the evaluation being commented on
            user_id: ID of the user creating the comment
            content: Comment content
            parent_comment_id: Optional ID of parent comment for replies
            **kwargs: Additional optional fields
        """
        self.evaluation_id = evaluation_id
        self.user_id = user_id
        self.content = content
        self.parent_comment_id = parent_comment_id

        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def edit(self, new_content: str) -> None:
        """Edit comment content

        Args:
            new_content: New content for the comment
        """
        if self.is_deleted:
            raise ValueError("Cannot edit a deleted comment")

        self.content = new_content
        self.is_edited = True
        self.edited_at = datetime.utcnow()
        db.session.commit()

    def soft_delete(self) -> None:
        """Soft delete the comment"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.content = "[Comment deleted]"
        db.session.commit()

    def restore(self) -> None:
        """Restore a soft-deleted comment"""
        if not self.is_deleted:
            return

        self.is_deleted = False
        self.deleted_at = None
        db.session.commit()

    @property
    def reply_count(self) -> int:
        """Get count of direct replies to this comment"""
        return self.replies.filter_by(is_deleted=False).count()

    @property
    def all_replies_count(self) -> int:
        """Get count of all nested replies"""
        count = 0
        for reply in self.replies.filter_by(is_deleted=False):
            count += 1 + reply.all_replies_count
        return count

    def get_reply_tree(self, max_depth: int = 5, current_depth: int = 0) -> list[dict]:
        """Get nested reply tree

        Args:
            max_depth: Maximum nesting depth to retrieve
            current_depth: Current depth in the tree

        Returns:
            List of reply dictionaries with nested replies
        """
        if current_depth >= max_depth:
            return []

        reply_tree = []
        for reply in self.replies.filter_by(is_deleted=False).order_by(
            Comment.created_at
        ):
            reply_dict = reply.to_dict()
            reply_dict["replies"] = reply.get_reply_tree(max_depth, current_depth + 1)
            reply_tree.append(reply_dict)

        return reply_tree

    @staticmethod
    def create_with_mentions(
        evaluation_id: int,
        user_id: int,
        content: str,
        mentioned_usernames: list[str] = None,
        parent_comment_id: int | None = None,
    ) -> "Comment":
        """Create comment and process mentions

        Args:
            evaluation_id: ID of the evaluation
            user_id: ID of the commenting user
            content: Comment content
            mentioned_usernames: List of mentioned usernames
            parent_comment_id: Optional parent comment ID

        Returns:
            Created Comment object
        """
        from app.models.mention import Mention

        # Create the comment
        comment = Comment(
            evaluation_id=evaluation_id,
            user_id=user_id,
            content=content,
            parent_comment_id=parent_comment_id,
        )

        db.session.add(comment)
        db.session.flush()  # Get the comment ID without committing

        # Process mentions if any
        if mentioned_usernames:
            for username in mentioned_usernames:
                # Create mentions using the Mention model's process method
                Mention.process_mentions(
                    text=content,
                    mentioner_id=user_id,
                    evaluation_id=evaluation_id,
                    comment_id=comment.id,
                    mention_type="evaluation_comment",
                )

        db.session.commit()
        return comment

    def to_dict(
        self, include_replies: bool = False, include_user: bool = True
    ) -> dict[str, Any]:
        """Convert comment to dictionary

        Args:
            include_replies: Whether to include nested replies
            include_user: Whether to include user information

        Returns:
            Comment data dictionary
        """
        data = {
            "id": self.id,
            "evaluation_id": self.evaluation_id,
            "user_id": self.user_id,
            "parent_comment_id": self.parent_comment_id,
            "content": self.content,
            "is_edited": self.is_edited,
            "edited_at": self.edited_at.isoformat() if self.edited_at else None,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "reply_count": self.reply_count if not self.is_deleted else 0,
        }

        if include_user and self.user:
            data["user_name"] = self.user.full_name
            data["user_username"] = self.user.username
            data["user_avatar"] = getattr(self.user, "avatar", None)
            data["user_role"] = self.user.role

        if include_replies and not self.is_deleted:
            data["replies"] = self.get_reply_tree()

        # Include mention count
        data["mention_count"] = self.mentions.count() if self.mentions else 0

        return data

    def __repr__(self) -> str:
        return f"<Comment {self.id} by User {self.user_id} on Evaluation {self.evaluation_id}>"

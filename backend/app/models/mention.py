"""Mention model for @mention functionality in Solution Evaluation System

This model tracks when users are mentioned in evaluations, comments, or messages,
enabling notification and tracking of user mentions across the system.
"""

from datetime import datetime
from enum import Enum

from app import db


class MentionType(Enum):
    """Mention type enumeration"""

    EVALUATION_COMMENT = "evaluation_comment"
    EVALUATION_DESCRIPTION = "evaluation_description"
    MESSAGE = "message"
    TASK_ASSIGNMENT = "task_assignment"


class MentionStatus(Enum):
    """Mention status enumeration"""

    UNREAD = "unread"
    READ = "read"
    ACKNOWLEDGED = "acknowledged"


class Mention(db.Model):
    """Model for tracking @mentions of users in various contexts

    Used for:
    - Tracking mentions in evaluation comments
    - Tracking mentions in messages
    - Generating mention notifications
    - Managing mention acknowledgments
    """

    __tablename__ = "mentions"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Mention type
    mention_type = db.Column(
        db.Enum(
            "evaluation_comment",
            "evaluation_description",
            "message",
            "task_assignment",
            name="mention_types",
        ),
        nullable=False,
    )

    # Users involved
    mentioned_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    mentioner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Related entities (optional based on mention type)
    evaluation_id = db.Column(db.Integer, db.ForeignKey("evaluations.id"))
    message_id = db.Column(db.Integer, db.ForeignKey("messages.id"))
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"))

    # Context and content
    context_text = db.Column(db.Text)  # The text containing the mention
    mention_position = db.Column(
        db.Integer
    )  # Character position of the mention in context

    # Status tracking
    status = db.Column(
        db.Enum("unread", "read", "acknowledged", name="mention_status"),
        nullable=False,
        default="unread",
    )
    read_at = db.Column(db.DateTime)
    acknowledged_at = db.Column(db.DateTime)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    mentioned_user = db.relationship(
        "User",
        foreign_keys=[mentioned_user_id],
        backref=db.backref("mentions_received", lazy="dynamic"),
    )
    mentioner = db.relationship(
        "User",
        foreign_keys=[mentioner_id],
        backref=db.backref("mentions_made", lazy="dynamic"),
    )
    evaluation = db.relationship(
        "Evaluation", backref=db.backref("evaluation_mentions", lazy="dynamic")
    )
    message = db.relationship(
        "Message", backref=db.backref("message_mentions", lazy="dynamic")
    )
    comment = db.relationship(
        "Comment", backref=db.backref("comment_mentions", lazy="dynamic")
    )

    def __init__(
        self,
        mention_type: str,
        mentioned_user_id: int,
        mentioner_id: int,
        **kwargs,
    ):
        """Initialize mention with required fields

        Args:
            mention_type: Type of mention
            mentioned_user_id: ID of the user being mentioned
            mentioner_id: ID of the user creating the mention
            **kwargs: Additional optional fields

        """
        self.mention_type = mention_type
        self.mentioned_user_id = mentioned_user_id
        self.mentioner_id = mentioner_id

        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def mark_as_read(self):
        """Mark mention as read"""
        if self.status == "unread":
            self.status = "read"
            self.read_at = datetime.utcnow()
            db.session.commit()

    def acknowledge(self):
        """Acknowledge the mention"""
        if self.status != "acknowledged":
            self.status = "acknowledged"
            self.acknowledged_at = datetime.utcnow()
            if not self.read_at:
                self.read_at = datetime.utcnow()
            db.session.commit()

    @staticmethod
    def create_evaluation_mention(
        evaluation_id: int,
        mentioned_user_id: int,
        mentioner_id: int,
        context_text: str,
        mention_type: str = "evaluation_comment",
    ):
        """Create a mention in evaluation context

        Args:
            evaluation_id: ID of the evaluation
            mentioned_user_id: ID of the mentioned user
            mentioner_id: ID of the mentioning user
            context_text: Text containing the mention
            mention_type: Type of evaluation mention

        Returns:
            Mention: Created mention object

        """
        mention = Mention(
            mention_type=mention_type,
            mentioned_user_id=mentioned_user_id,
            mentioner_id=mentioner_id,
            evaluation_id=evaluation_id,
            context_text=context_text,
        )

        db.session.add(mention)
        db.session.commit()

        # Create notification for the mention
        # Delayed import to avoid circular dependency
        from app.models.message import Message

        Message.create_mention_notification(mention)

        return mention

    @staticmethod
    def extract_mentions(text: str) -> list[str]:
        """Extract @mentions from text

        Args:
            text: Text to parse for mentions

        Returns:
            list: List of mentioned usernames

        """
        import re

        # Pattern to match @username (alphanumeric and underscore)
        pattern = r"@(\w+)"
        mentions = re.findall(pattern, text)

        # Remove duplicates while preserving order
        seen = set()
        unique_mentions = []
        for mention in mentions:
            if mention not in seen:
                seen.add(mention)
                unique_mentions.append(mention)

        return unique_mentions

    @staticmethod
    def process_mentions(
        text: str,
        mentioner_id: int,
        evaluation_id: int = None,
        message_id: int = None,
        mention_type: str = "evaluation_comment",
    ) -> list:
        """Process text for mentions and create mention records

        Args:
            text: Text containing mentions
            mentioner_id: ID of the user creating mentions
            evaluation_id: Optional evaluation ID
            message_id: Optional message ID
            mention_type: Type of mention

        Returns:
            list: List of created Mention objects

        """
        from app.models.user import User

        # Extract mentioned usernames
        usernames = Mention.extract_mentions(text)
        if not usernames:
            return []

        created_mentions = []

        for username in usernames:
            # Find user by username
            user = User.query.filter_by(username=username).first()
            if user and user.id != mentioner_id:  # Don't create self-mentions
                # Find position of mention in text
                position = text.find(f"@{username}")

                mention = Mention(
                    mention_type=mention_type,
                    mentioned_user_id=user.id,
                    mentioner_id=mentioner_id,
                    evaluation_id=evaluation_id,
                    message_id=message_id,
                    context_text=text,
                    mention_position=position,
                )

                db.session.add(mention)
                created_mentions.append(mention)

        if created_mentions:
            db.session.commit()

            # Create notifications for all mentions
            # Delayed import to avoid circular dependency
            from app.models.message import Message

            for mention in created_mentions:
                Message.create_mention_notification(mention)

        return created_mentions

    def to_dict(self) -> dict:
        """Convert mention to dictionary

        Returns:
            dict: Mention data dictionary

        """
        return {
            "id": self.id,
            "mention_type": self.mention_type,
            "mentioned_user_id": self.mentioned_user_id,
            "mentioned_user_name": self.mentioned_user.full_name
            if self.mentioned_user
            else None,
            "mentioner_id": self.mentioner_id,
            "mentioner_name": self.mentioner.full_name if self.mentioner else None,
            "evaluation_id": self.evaluation_id,
            "evaluation_number": self.evaluation.evaluation_number
            if self.evaluation
            else None,
            "message_id": self.message_id,
            "context_text": self.context_text,
            "mention_position": self.mention_position,
            "status": self.status,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat()
            if self.acknowledged_at
            else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Mention @{self.mentioned_user.username if self.mentioned_user else 'unknown'} by {self.mentioner.username if self.mentioner else 'unknown'}>"

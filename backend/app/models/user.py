from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class UserRole(Enum):
    """User role enumeration."""

    ADMIN = "admin"
    GROUP_LEADER = "group_leader"
    PART_LEADER = "part_leader"
    USER = "user"


class User(db.Model):
    """User model for authentication and authorization.

    Roles hierarchy (from highest to lowest):
    - admin: System administrator with full access
    - group_leader: Group leader with approval rights
    - part_leader: Part leader with initial approval rights
    - user: Regular user with basic access
    """

    __tablename__ = "users"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Basic user information
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # User profile
    full_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))  # New field for user's position/title
    phone = db.Column(db.String(20))

    # Role and status
    role = db.Column(
        db.Enum("admin", "group_leader", "part_leader", "user", name="user_roles"),
        nullable=False,
        default="user",
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_login = db.Column(db.DateTime)

    # Relationships
    evaluations = db.relationship(
        "Evaluation",
        foreign_keys="Evaluation.evaluator_id",
        backref="evaluator",
        lazy="dynamic",
    )
    part_approvals = db.relationship(
        "Evaluation",
        foreign_keys="Evaluation.part_approver_id",
        backref="part_approver",
        lazy="dynamic",
    )
    group_approvals = db.relationship(
        "Evaluation",
        foreign_keys="Evaluation.group_approver_id",
        backref="group_approver",
        lazy="dynamic",
    )
    messages = db.relationship(
        "Message",
        foreign_keys="Message.recipient_id",
        backref="recipient",
        lazy="dynamic",
    )
    sent_messages = db.relationship(
        "Message", foreign_keys="Message.sender_id", backref="sender", lazy="dynamic"
    )
    operation_logs = db.relationship("OperationLog", backref="user", lazy="dynamic")

    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role: str = "user",
        **kwargs: Any,
    ) -> None:
        """Initialize user with required fields.

        Args:
            username: Unique username.
            email: User email address.
            password: Plain text password (will be hashed).
            full_name: User's full name.
            role: User role. Defaults to 'user'.
            **kwargs: Additional optional fields.

        """
        self.username = username
        self.email = email
        self.set_password(password)
        self.full_name = full_name
        self.role = role

        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def set_password(self, password: str) -> None:
        """Hash and set user password.

        Args:
            password: Plain text password.

        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify user password.

        Args:
            password: Plain text password to verify.

        Returns:
            True if password matches, False otherwise.

        """
        return check_password_hash(self.password_hash, password)

    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def has_permission(self, required_role: str) -> bool:
        """Check if user has required permission level.

        Args:
            required_role: Required role level.

        Returns:
            True if user has permission, False otherwise.

        """
        role_hierarchy: dict[str, int] = {
            "user": 1,
            "part_leader": 2,
            "group_leader": 3,
            "admin": 4,
        }

        user_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        return user_level >= required_level

    def can_approve_evaluation(self, evaluation_type: str) -> bool:
        """Check if user can approve specific evaluation type.

        Args:
            evaluation_type: Type of evaluation.

        Returns:
            True if user can approve, False otherwise.

        """
        if evaluation_type == "new_product":
            # New solution evaluations require part_leader or higher
            return self.has_permission("part_leader")
        elif evaluation_type == "mass_production":
            # Mass production evaluations don't require approval
            return False

        return False

    def to_dict(self, include_sensitive: bool = False) -> dict[str, Any]:
        """Convert user object to dictionary.

        Args:
            include_sensitive: Whether to include sensitive information.

        Returns:
            User data dictionary.

        """
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "department": self.department,
            "position": self.position,
            "phone": self.phone,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

        if include_sensitive:
            data["password_hash"] = self.password_hash

        return data

    def __repr__(self) -> str:
        return f"<User {self.username}>"

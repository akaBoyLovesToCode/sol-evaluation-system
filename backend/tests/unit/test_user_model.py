"""Unit tests for the User model.
"""

import pytest
from app.models.user import User, UserRole


def test_user_creation(session):
    """Test creating a new user."""
    user = User(
        username="testuser",
        email="test@example.com",
        password="Password123", 
        full_name="Test User",
        role=UserRole.USER.value,
    )
    session.add(user)
    session.commit()

    # Retrieve the user from the database
    retrieved_user = session.query(User).filter_by(username="testuser").first()

    assert retrieved_user is not None
    assert retrieved_user.username == "testuser"
    assert retrieved_user.email == "test@example.com"
    assert retrieved_user.full_name == "Test User"
    assert retrieved_user.role == UserRole.USER.value
    assert retrieved_user.check_password("Password123") is True
    assert retrieved_user.check_password("WrongPassword") is False


def test_user_role_validation():
    """Test that user roles are validated correctly."""
    # Valid role
    user = User(
        username="roleuser",
        email="role@example.com",
        password="Password123",
        full_name="Role User",
        role=UserRole.ADMIN.value,
    )
    assert user.role == UserRole.ADMIN.value

    # Test setting role to valid value
    user.role = UserRole.USER.value
    assert user.role == UserRole.USER.value


def test_user_profile_fields(session):
    """Test user profile fields."""
    user = User(
        username="profileuser",
        email="profile@example.com",
        password="Password123",
        full_name="Profile User",
        role=UserRole.USER.value,
        department="Engineering",
        position="Developer",
    )
    session.add(user)
    session.commit()

    # Retrieve the user from the database
    retrieved_user = session.query(User).filter_by(username="profileuser").first()

    assert retrieved_user is not None
    assert retrieved_user.department == "Engineering"
    assert retrieved_user.position == "Developer"


def test_user_to_dict(session):
    """Test the to_dict method of the User model."""
    user = User(
        username="dictuser",
        email="dict@example.com",
        password="Password123",
        full_name="Dict User",
        role=UserRole.USER.value,
        department="Marketing",
        position="Manager",
    )
    session.add(user)
    session.commit()

    user_dict = user.to_dict()

    assert user_dict["username"] == "dictuser"
    assert user_dict["email"] == "dict@example.com"
    assert user_dict["full_name"] == "Dict User"
    assert user_dict["role"] == UserRole.USER.value
    assert user_dict["department"] == "Marketing"
    assert user_dict["position"] == "Manager"
    assert "password_hash" not in user_dict  # Ensure sensitive data is not included

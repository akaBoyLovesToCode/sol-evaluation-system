"""Unit tests for the OperationLog model and functionality."""

from app.models.operation_log import OperationLog, OperationType


def test_operation_log_creation(session, admin_user):
    """Test creating a new operation log."""
    log = OperationLog(
        user_id=admin_user.id,
        operation_type=OperationType.CREATE.value,
        target_type="evaluation",
        target_id=1,
        target_description="Created evaluation EV-20250101-001",
        operation_description="Created a new evaluation",
        ip_address="127.0.0.1",
        user_agent="Test Agent",
        success=True,
    )
    session.add(log)
    session.commit()

    # Retrieve the log from the database
    retrieved_log = session.query(OperationLog).filter_by(user_id=admin_user.id).first()

    assert retrieved_log is not None
    assert retrieved_log.user_id == admin_user.id
    assert retrieved_log.operation_type == OperationType.CREATE.value
    assert retrieved_log.target_type == "evaluation"
    assert retrieved_log.target_id == 1
    assert retrieved_log.target_description == "Created evaluation EV-20250101-001"
    assert retrieved_log.operation_description == "Created a new evaluation"
    assert retrieved_log.ip_address == "127.0.0.1"
    assert retrieved_log.user_agent == "Test Agent"
    assert retrieved_log.success is True


def test_operation_log_to_dict(session, admin_user):
    """Test the to_dict method of the OperationLog model."""
    test_data = {"key": "value", "number": 123}

    log = OperationLog(
        user_id=admin_user.id,
        operation_type=OperationType.UPDATE.value,
        target_type="user",
        target_id=admin_user.id,
        target_description="Updated user profile",
        operation_description="Updated user information",
        new_data=test_data,
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0",
        success=True,
    )
    session.add(log)
    session.commit()

    log_dict = log.to_dict()

    assert log_dict["user_id"] == admin_user.id
    assert log_dict["operation_type"] == OperationType.UPDATE.value
    assert log_dict["target_type"] == "user"
    assert log_dict["target_id"] == admin_user.id
    assert log_dict["target_description"] == "Updated user profile"
    assert log_dict["operation_description"] == "Updated user information"
    assert log_dict["new_data"] == test_data
    assert log_dict["ip_address"] == "192.168.1.1"
    assert log_dict["user_agent"] == "Mozilla/5.0"
    assert log_dict["success"] is True
    assert "created_at" in log_dict

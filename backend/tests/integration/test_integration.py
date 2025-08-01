"""Integration tests for the entire application.
"""

import pytest
from flask import url_for
from app.models.user import User, UserRole
from app.models.evaluation import Evaluation, EvaluationStatus, EvaluationType
from app.models.operation_log import OperationLog
from tests.helpers import create_test_evaluation, json_response
from datetime import datetime, timedelta


def test_user_profile_flow(client, session, regular_user, user_headers):
    """Test the complete user profile update flow."""
    # Get the user profile
    response = client.get("/api/users/profile", headers=user_headers)
    assert response.status_code == 200
    data = json_response(response)
    assert data["success"] is True
    assert data["data"]["user"]["username"] == regular_user.username

    # Update the user profile
    update_data = {
        "fullName": "Updated Name",
        "email": "updated@example.com",
        "department": "Engineering",
        "position": "Senior Developer",
    }

    response = client.put("/api/users/profile", headers=user_headers, json=update_data)
    assert response.status_code == 200
    data = json_response(response)
    assert data["success"] is True
    assert data["data"]["user"]["fullName"] == update_data["fullName"]
    assert data["data"]["user"]["email"] == update_data["email"]
    assert data["data"]["user"]["department"] == update_data["department"]
    assert data["data"]["user"]["position"] == update_data["position"]

    # Change the user password
    password_data = {"currentPassword": "Password123", "newPassword": "NewPassword123"}

    response = client.put(
        "/api/users/password", headers=user_headers, json=password_data
    )
    assert response.status_code == 200
    data = json_response(response)
    assert data["success"] is True

    # Verify that the password was changed
    updated_user = User.query.get(regular_user.id)
    assert updated_user.check_password("NewPassword123") is True
    assert updated_user.check_password("Password123") is False

    # Verify that operation logs were created
    logs = OperationLog.query.filter_by(user_id=regular_user.id).all()
    assert len(logs) >= 2  # At least one for profile update and one for password change


def test_evaluation_lifecycle(
    client, session, regular_user, user_headers, admin_user, admin_headers
):
    """Test the complete evaluation lifecycle."""
    # Create a new evaluation
    evaluation_data = {
        "evaluation_number": f"EV-{datetime.now().strftime('%Y%m%d')}-TEST",
        "evaluation_type": EvaluationType.NEW_PRODUCT.value,
        "product_name": "Lifecycle Test Product",
        "part_number": "LTP-001",
        "evaluation_reason": "Testing Lifecycle",
        "description": "Testing the complete evaluation lifecycle",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "expected_end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "process_step": "M001",
    }

    response = client.post(
        "/api/evaluations", headers=user_headers, json=evaluation_data
    )
    assert response.status_code == 201
    data = json_response(response)
    assert data["success"] is True
    evaluation_id = data["data"]["evaluation"]["id"]

    # Update the evaluation
    update_data = {
        "product_name": "Updated Lifecycle Test Product",
        "description": "Updated description for lifecycle test",
        "process_step": "M002",
    }

    response = client.put(
        f"/api/evaluations/{evaluation_id}", headers=user_headers, json=update_data
    )
    assert response.status_code == 200
    data = json_response(response)
    assert data["success"] is True
    assert data["data"]["evaluation"]["product_name"] == update_data["product_name"]
    assert data["data"]["evaluation"]["process_step"] == update_data["process_step"]

    # Change the status to in_progress
    status_data = {"status": EvaluationStatus.IN_PROGRESS.value}

    response = client.put(
        f"/api/evaluations/{evaluation_id}/status",
        headers=user_headers,
        json=status_data,
    )
    assert response.status_code == 200
    data = json_response(response)
    assert data["success"] is True
    assert data["data"]["evaluation"]["status"] == EvaluationStatus.IN_PROGRESS.value

    # Pause the evaluation
    status_data = {"status": EvaluationStatus.PAUSED.value}

    response = client.put(
        f"/api/evaluations/{evaluation_id}/status",
        headers=user_headers,
        json=status_data,
    )
    assert response.status_code == 200
    data = json_response(response)
    assert data["success"] is True
    assert data["data"]["evaluation"]["status"] == EvaluationStatus.PAUSED.value

    # Resume the evaluation
    status_data = {"status": EvaluationStatus.IN_PROGRESS.value}

    response = client.put(
        f"/api/evaluations/{evaluation_id}/status",
        headers=user_headers,
        json=status_data,
    )
    assert response.status_code == 200
    data = json_response(response)
    assert data["success"] is True
    assert data["data"]["evaluation"]["status"] == EvaluationStatus.IN_PROGRESS.value

    # Complete the evaluation
    status_data = {"status": EvaluationStatus.COMPLETED.value}

    response = client.put(
        f"/api/evaluations/{evaluation_id}/status",
        headers=user_headers,
        json=status_data,
    )
    assert response.status_code == 200
    data = json_response(response)
    assert data["success"] is True
    assert data["data"]["evaluation"]["status"] == EvaluationStatus.COMPLETED.value
    assert data["data"]["evaluation"]["actual_end_date"] is not None

    # Get the evaluation logs
    response = client.get(
        f"/api/evaluations/{evaluation_id}/logs", headers=admin_headers
    )
    assert response.status_code == 200
    data = json_response(response)
    assert data["success"] is True
    assert len(data["data"]["logs"]) >= 5  # At least one log for each operation


def test_admin_user_management(client, session, admin_user, admin_headers):
    """Test the complete admin user management flow."""
    # Create a new user
    user_data = {
        "username": "testadmin",
        "email": "testadmin@example.com",
        "fullName": "Test Admin",
        "password": "Password123",
        "role": UserRole.ADMIN.value,
        "department": "IT",
        "position": "System Administrator",
        "is_active": True,
    }

    response = client.post("/api/users", headers=admin_headers, json=user_data)
    assert response.status_code == 201
    data = json_response(response)
    assert data["success"] is True
    user_id = data["data"]["user"]["id"]

    # Update the user
    update_data = {
        "fullName": "Updated Test Admin",
        "email": "updated.testadmin@example.com",
        "department": "Information Technology",
        "position": "Senior System Administrator",
        "role": UserRole.ADMIN.value,
    }

    response = client.put(
        f"/api/users/{user_id}", headers=admin_headers, json=update_data
    )
    assert response.status_code == 200
    data = json_response(response)
    assert data["success"] is True
    assert data["data"]["user"]["fullName"] == update_data["fullName"]
    assert data["data"]["user"]["email"] == update_data["email"]
    assert data["data"]["user"]["department"] == update_data["department"]
    assert data["data"]["user"]["position"] == update_data["position"]

    # Deactivate the user
    status_data = {"is_active": False}

    response = client.put(
        f"/api/users/{user_id}/status", headers=admin_headers, json=status_data
    )
    assert response.status_code == 200
    data = json_response(response)
    assert data["success"] is True
    assert data["data"]["user"]["is_active"] is False

    # Activate the user
    status_data = {"is_active": True}

    response = client.put(
        f"/api/users/{user_id}/status", headers=admin_headers, json=status_data
    )
    assert response.status_code == 200
    data = json_response(response)
    assert data["success"] is True
    assert data["data"]["user"]["is_active"] is True

    # Delete the user
    response = client.delete(f"/api/users/{user_id}", headers=admin_headers)
    assert response.status_code == 200
    data = json_response(response)
    assert data["success"] is True

    # Verify that the user was deleted
    deleted_user = User.query.get(user_id)
    assert deleted_user is None

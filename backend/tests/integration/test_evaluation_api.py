"""Integration tests for the evaluation API endpoints.
"""

import json
import pytest
from datetime import datetime, timedelta
from flask import url_for
from app.models.evaluation import Evaluation, EvaluationStatus, EvaluationType
from tests.helpers import create_test_evaluation, json_response


def test_get_evaluations(client, session, regular_user, user_headers):
    """Test getting a list of evaluations."""
    # Create some test evaluations
    for i in range(3):
        create_test_evaluation(
            session,
            regular_user.id,
            evaluation_number=f"EV-{datetime.now().strftime('%Y%m%d')}-{i + 1:03d}",
            product_name=f"Test Product {i + 1}",
        )

    # Get the evaluations
    response = client.get("/api/evaluations", headers=user_headers)

    assert response.status_code == 200
    data = json_response(response)
    assert "evaluations" in data["data"]
    assert len(data["data"]["evaluations"]) == 3


def test_get_evaluation_detail(client, session, regular_user, user_headers):
    """Test getting details of a specific evaluation."""
    # Create a test evaluation
    evaluation = create_test_evaluation(session, regular_user.id)

    # Get the evaluation details
    response = client.get(f"/api/evaluations/{evaluation.id}", headers=user_headers)

    assert response.status_code == 200
    data = json_response(response)
    assert "evaluation" in data["data"]
    assert data["data"]["evaluation"]["id"] == evaluation.id
    assert (
        data["data"]["evaluation"]["evaluation_number"] == evaluation.evaluation_number
    )
    assert data["data"]["evaluation"]["product_name"] == evaluation.product_name
    assert data["data"]["evaluation"]["process_step"] == evaluation.process_step
    assert "expected_end_date" in data["data"]["evaluation"]


def test_create_evaluation(client, session, regular_user, user_headers):
    """Test creating a new evaluation."""
    # Prepare evaluation data
    evaluation_data = {
        "evaluation_number": f"EV-{datetime.now().strftime('%Y%m%d')}-NEW",
        "evaluation_type": EvaluationType.NEW_PRODUCT.value,
        "product_name": "New Test Product",
        "part_number": "NTP-001",
        "evaluation_reason": "Testing API",
        "description": "Test evaluation creation via API",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "expected_end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "process_step": "M002",
    }

    # Create the evaluation
    response = client.post(
        "/api/evaluations", headers=user_headers, json=evaluation_data
    )

    assert response.status_code == 201
    data = json_response(response)
    assert "evaluation" in data["data"]
    assert (
        data["data"]["evaluation"]["evaluation_number"]
        == evaluation_data["evaluation_number"]
    )
    assert data["data"]["evaluation"]["product_name"] == evaluation_data["product_name"]
    assert data["data"]["evaluation"]["process_step"] == evaluation_data["process_step"]
    assert data["data"]["evaluation"]["expected_end_date"] is not None

    # Verify that the evaluation was created in the database
    evaluation = (
        session.query(Evaluation)
        .filter_by(evaluation_number=evaluation_data["evaluation_number"])
        .first()
    )
    assert evaluation is not None
    assert evaluation.product_name == evaluation_data["product_name"]
    assert evaluation.process_step == evaluation_data["process_step"]
    assert evaluation.expected_end_date is not None


def test_create_evaluation_auto_generated_number(
    client, session, regular_user, user_headers
):
    """Test creating a new evaluation with auto-generated evaluation number."""
    # Prepare evaluation data WITHOUT evaluation_number
    evaluation_data = {
        "evaluation_type": EvaluationType.NEW_PRODUCT.value,
        "product_name": "Auto Generated Test Product",
        "part_number": "AGTP-001",
        "evaluation_reason": "Testing auto-generation",
        "description": "Test evaluation number auto-generation",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "expected_end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "process_step": "M001",
    }

    # Create the evaluation
    response = client.post(
        "/api/evaluations", headers=user_headers, json=evaluation_data
    )

    assert response.status_code == 201
    data = json_response(response)
    assert "evaluation" in data["data"]

    # Check that evaluation_number was auto-generated in correct format
    evaluation_number = data["data"]["evaluation"]["evaluation_number"]
    assert evaluation_number is not None
    assert evaluation_number.startswith("EVAL-")
    assert len(evaluation_number) == 17  # EVAL-YYYYMMDD-NNNN format

    # Verify the format matches EVAL-YYYYMMDD-NNNN
    import re

    pattern = r"^EVAL-\d{8}-\d{4}$"
    assert re.match(pattern, evaluation_number)

    # Verify that the evaluation was created in the database
    evaluation = (
        session.query(Evaluation).filter_by(evaluation_number=evaluation_number).first()
    )
    assert evaluation is not None
    assert evaluation.product_name == evaluation_data["product_name"]


def test_create_evaluation_with_status(client, session, regular_user, user_headers):
    """Test creating a new evaluation with specified status."""
    # Test with draft status
    draft_data = {
        "evaluation_type": EvaluationType.MASS_PRODUCTION.value,
        "product_name": "Draft Status Test",
        "part_number": "DST-001",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "expected_end_date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
        "process_step": "M001",
        "status": "draft",
    }

    response = client.post("/api/evaluations", headers=user_headers, json=draft_data)
    assert response.status_code == 201
    data = json_response(response)
    assert data["data"]["evaluation"]["status"] == "draft"

    # Test with in_progress status
    in_progress_data = {
        "evaluation_type": EvaluationType.NEW_PRODUCT.value,
        "product_name": "In Progress Status Test",
        "part_number": "IPST-001",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "expected_end_date": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
        "process_step": "M002",
        "status": "in_progress",
    }

    response = client.post(
        "/api/evaluations", headers=user_headers, json=in_progress_data
    )
    assert response.status_code == 201
    data = json_response(response)
    assert data["data"]["evaluation"]["status"] == "in_progress"


def test_create_multiple_evaluations_same_day(
    client, session, regular_user, user_headers
):
    """Test creating multiple evaluations on the same day to verify number incrementing."""
    evaluations = []

    # Create 3 evaluations on the same day
    for i in range(3):
        evaluation_data = {
            "evaluation_type": EvaluationType.NEW_PRODUCT.value,
            "product_name": f"Sequential Test Product {i + 1}",
            "part_number": f"STP-{i + 1:03d}",
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "expected_end_date": (datetime.now() + timedelta(days=30)).strftime(
                "%Y-%m-%d"
            ),
            "process_step": "M001",
        }

        response = client.post(
            "/api/evaluations", headers=user_headers, json=evaluation_data
        )
        assert response.status_code == 201
        data = json_response(response)
        evaluations.append(data["data"]["evaluation"]["evaluation_number"])

    # Verify that the numbers are sequential
    today_prefix = f"EVAL-{datetime.now().strftime('%Y%m%d')}-"

    # Extract the numbers and verify they are different and increasing
    numbers = []
    for eval_num in evaluations:
        assert eval_num.startswith(today_prefix)
        number_part = int(eval_num.split("-")[-1])
        numbers.append(number_part)

    # Check that numbers are sequential (allowing for existing evaluations)
    assert len(set(numbers)) == 3  # All numbers should be unique
    assert numbers[1] == numbers[0] + 1
    assert numbers[2] == numbers[1] + 1


def test_update_evaluation(client, session, regular_user, user_headers):
    """Test updating an existing evaluation."""
    # Create a test evaluation
    evaluation = create_test_evaluation(
        session, regular_user.id, status=EvaluationStatus.IN_PROGRESS.value
    )

    # Prepare update data
    update_data = {
        "product_name": "Updated Product Name",
        "description": "Updated description",
        "expected_end_date": (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"),
        "process_step": "M003",
    }

    # Update the evaluation
    response = client.put(
        f"/api/evaluations/{evaluation.id}", headers=user_headers, json=update_data
    )

    assert response.status_code == 200
    data = json_response(response)
    assert data["data"]["evaluation"]["product_name"] == update_data["product_name"]
    assert data["data"]["evaluation"]["description"] == update_data["description"]
    assert data["data"]["evaluation"]["process_step"] == update_data["process_step"]

    # Verify that the evaluation was updated in the database
    updated_evaluation = session.query(Evaluation).filter_by(id=evaluation.id).first()
    assert updated_evaluation.product_name == update_data["product_name"]
    assert updated_evaluation.description == update_data["description"]
    assert updated_evaluation.process_step == update_data["process_step"]


def test_update_evaluation_status(client, session, regular_user, user_headers):
    """Test updating the status of an evaluation."""
    # Create a test evaluation
    evaluation = create_test_evaluation(
        session, regular_user.id, status=EvaluationStatus.IN_PROGRESS.value
    )

    # Prepare status update data
    status_data = {"status": EvaluationStatus.PAUSED.value}

    # Update the evaluation status
    response = client.put(
        f"/api/evaluations/{evaluation.id}/status",
        headers=user_headers,
        json=status_data,
    )

    assert response.status_code == 200
    data = json_response(response)
    assert data["data"]["evaluation"]["status"] == EvaluationStatus.PAUSED.value

    # Verify that the evaluation status was updated in the database
    updated_evaluation = session.query(Evaluation).filter_by(id=evaluation.id).first()
    assert updated_evaluation.status == EvaluationStatus.PAUSED.value


def test_complete_evaluation(client, session, regular_user, user_headers):
    """Test completing an evaluation."""
    # Create a test evaluation
    evaluation = create_test_evaluation(
        session, regular_user.id, status=EvaluationStatus.IN_PROGRESS.value
    )

    # Prepare status update data
    status_data = {"status": EvaluationStatus.COMPLETED.value}

    # Complete the evaluation
    response = client.put(
        f"/api/evaluations/{evaluation.id}/status",
        headers=user_headers,
        json=status_data,
    )

    assert response.status_code == 200
    data = json_response(response)
    assert data["data"]["evaluation"]["status"] == EvaluationStatus.COMPLETED.value
    assert data["data"]["evaluation"]["actual_end_date"] is not None

    # Verify that the evaluation was completed in the database
    completed_evaluation = session.query(Evaluation).filter_by(id=evaluation.id).first()
    assert completed_evaluation.status == EvaluationStatus.COMPLETED.value
    assert completed_evaluation.actual_end_date is not None


def test_get_evaluation_logs(client, session, regular_user, admin_user, admin_headers):
    """Test getting operation logs for an evaluation."""
    # Create a test evaluation
    evaluation = create_test_evaluation(session, regular_user.id)

    # Get the evaluation logs
    response = client.get(
        f"/api/evaluations/{evaluation.id}/logs", headers=admin_headers
    )

    assert response.status_code == 200
    data = json_response(response)
    assert "logs" in data["data"]
    # There should be at least one log entry for the creation of the evaluation
    assert len(data["data"]["logs"]) >= 1

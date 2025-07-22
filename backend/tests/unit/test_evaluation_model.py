"""
Unit tests for the Evaluation model.
"""

import pytest
import re
from datetime import datetime, timedelta
from app.models.evaluation import Evaluation, EvaluationType, EvaluationStatus
from app.models.user import User, UserRole
from app.api.evaluation import generate_evaluation_number
from tests.helpers import create_test_evaluation


def test_evaluation_creation(session, regular_user):
    """Test creating a new evaluation."""
    start_date = datetime.now().date()
    expected_end_date = (datetime.now() + timedelta(days=30)).date()

    evaluation = Evaluation(
        evaluation_number="EV-20250101-001",
        evaluation_type=EvaluationType.NEW_PRODUCT.value,
        product_name="Test Product",
        part_number="TP-001",
        evaluation_reason="Testing",
        description="Test evaluation description",
        status=EvaluationStatus.DRAFT.value,
        start_date=start_date,
        expected_end_date=expected_end_date,
        process_step="M001",
        evaluator_id=regular_user.id,
    )
    session.add(evaluation)
    session.commit()

    # Retrieve the evaluation from the database
    retrieved_evaluation = (
        session.query(Evaluation).filter_by(evaluation_number="EV-20250101-001").first()
    )

    assert retrieved_evaluation is not None
    assert retrieved_evaluation.evaluation_number == "EV-20250101-001"
    assert retrieved_evaluation.evaluation_type == EvaluationType.NEW_PRODUCT.value
    assert retrieved_evaluation.product_name == "Test Product"
    assert retrieved_evaluation.part_number == "TP-001"
    assert retrieved_evaluation.evaluation_reason == "Testing"
    assert retrieved_evaluation.description == "Test evaluation description"
    assert retrieved_evaluation.status == EvaluationStatus.DRAFT.value
    assert retrieved_evaluation.start_date == start_date
    assert retrieved_evaluation.expected_end_date == expected_end_date
    assert retrieved_evaluation.process_step == "M001"
    assert retrieved_evaluation.evaluator_id == regular_user.id


def test_evaluation_status_validation():
    """Test that evaluation status is validated correctly."""
    # Valid status
    evaluation = Evaluation(
        evaluation_number="EV-20250101-002",
        evaluation_type=EvaluationType.NEW_PRODUCT.value,
        product_name="Status Test",
        part_number="ST-001",
        status=EvaluationStatus.IN_PROGRESS.value,
        start_date=datetime.now().date(),
    )
    assert evaluation.status == EvaluationStatus.IN_PROGRESS.value

    # Invalid status
    with pytest.raises(ValueError):
        Evaluation(
            evaluation_number="EV-20250101-003",
            evaluation_type=EvaluationType.NEW_PRODUCT.value,
            product_name="Invalid Status",
            part_number="IS-001",
            status="invalid_status",
            start_date=datetime.now().date(),
        )


def test_evaluation_type_validation():
    """Test that evaluation type is validated correctly."""
    # Valid type
    evaluation = Evaluation(
        evaluation_number="EV-20250101-004",
        evaluation_type=EvaluationType.MASS_PRODUCTION.value,
        product_name="Type Test",
        part_number="TT-001",
        status=EvaluationStatus.DRAFT.value,
        start_date=datetime.now().date(),
    )
    assert evaluation.evaluation_type == EvaluationType.MASS_PRODUCTION.value

    # Invalid type
    with pytest.raises(ValueError):
        Evaluation(
            evaluation_number="EV-20250101-005",
            evaluation_type="invalid_type",
            product_name="Invalid Type",
            part_number="IT-001",
            status=EvaluationStatus.DRAFT.value,
            start_date=datetime.now().date(),
        )


def test_evaluation_to_dict(session, regular_user):
    """Test the to_dict method of the Evaluation model."""
    evaluation = create_test_evaluation(session, regular_user.id)

    evaluation_dict = evaluation.to_dict()

    assert evaluation_dict["evaluation_number"] == evaluation.evaluation_number
    assert evaluation_dict["evaluation_type"] == evaluation.evaluation_type
    assert evaluation_dict["product_name"] == evaluation.product_name
    assert evaluation_dict["part_number"] == evaluation.part_number
    assert evaluation_dict["evaluation_reason"] == evaluation.evaluation_reason
    assert evaluation_dict["description"] == evaluation.description
    assert evaluation_dict["status"] == evaluation.status
    assert evaluation_dict["process_step"] == evaluation.process_step
    assert "start_date" in evaluation_dict
    assert "expected_end_date" in evaluation_dict


def test_evaluation_relationships(session, regular_user):
    """Test the relationships of the Evaluation model."""
    evaluation = create_test_evaluation(session, regular_user.id)

    # Test evaluator relationship
    assert evaluation.evaluator is not None
    assert evaluation.evaluator.id == regular_user.id
    assert evaluation.evaluator.username == regular_user.username


def test_generate_evaluation_number_format(app_context):
    """Test that generated evaluation numbers follow the correct format."""
    eval_number = generate_evaluation_number()

    # Check format: EVAL-YYYYMMDD-NNNN
    assert eval_number.startswith("EVAL-")
    assert len(eval_number) == 17

    # Verify regex pattern
    pattern = r"^EVAL-\d{8}-\d{4}$"
    assert re.match(pattern, eval_number)

    # Verify date part matches today
    today_str = datetime.now().strftime("%Y%m%d")
    expected_prefix = f"EVAL-{today_str}-"
    assert eval_number.startswith(expected_prefix)


def test_generate_evaluation_number_uniqueness(app_context, session):
    """Test that generated evaluation numbers are unique."""
    # Generate multiple numbers
    numbers = []
    for i in range(5):
        eval_number = generate_evaluation_number()
        numbers.append(eval_number)

        # Create a fake evaluation to increment the counter
        fake_eval = Evaluation(
            evaluation_number=eval_number,
            evaluation_type=EvaluationType.NEW_PRODUCT.value,
            product_name=f"Test {i}",
            part_number=f"T-{i}",
            status=EvaluationStatus.DRAFT.value,
            start_date=datetime.now().date(),
            expected_end_date=(datetime.now() + timedelta(days=30)).date(),
            process_step="M001",
            evaluator_id=1,  # Assuming user ID 1 exists
        )
        session.add(fake_eval)
        session.commit()

    # All numbers should be unique
    assert len(set(numbers)) == 5

    # Numbers should be sequential
    today_prefix = f"EVAL-{datetime.now().strftime('%Y%m%d')}-"
    extracted_numbers = []
    for num in numbers:
        number_part = int(num.replace(today_prefix, ""))
        extracted_numbers.append(number_part)

    # Check they are consecutive
    for i in range(1, len(extracted_numbers)):
        assert extracted_numbers[i] == extracted_numbers[i - 1] + 1


def test_generate_evaluation_number_with_existing_evaluations(
    app_context, session, regular_user
):
    """Test evaluation number generation when evaluations already exist for the day."""
    today_str = datetime.now().strftime("%Y%m%d")

    # Create some existing evaluations for today
    existing_numbers = [f"EVAL-{today_str}-0005", f"EVAL-{today_str}-0007"]

    for eval_num in existing_numbers:
        evaluation = Evaluation(
            evaluation_number=eval_num,
            evaluation_type=EvaluationType.NEW_PRODUCT.value,
            product_name="Existing Test",
            part_number="ET-001",
            status=EvaluationStatus.DRAFT.value,
            start_date=datetime.now().date(),
            expected_end_date=(datetime.now() + timedelta(days=30)).date(),
            process_step="M001",
            evaluator_id=regular_user.id,
        )
        session.add(evaluation)
    session.commit()

    # Generate a new number
    new_number = generate_evaluation_number()

    # Should be higher than the highest existing number
    expected = f"EVAL-{today_str}-0008"
    assert new_number == expected

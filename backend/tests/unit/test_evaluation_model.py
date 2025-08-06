"""Unit tests for the Evaluation model."""

from datetime import datetime, timedelta

from app.models.evaluation import Evaluation, EvaluationStatus, EvaluationType
from tests.helpers import create_test_evaluation


def test_evaluation_creation(session, regular_user):
    """Test creating a new evaluation."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    start_date = datetime.now().date()
    expected_end_date = (datetime.now() + timedelta(days=30)).date()

    evaluation = Evaluation(
        evaluation_number=f"EV-{datetime.now().strftime('%Y%m%d')}-{unique_id}",
        evaluation_type=EvaluationType.NEW_PRODUCT.value,
        product_name="Test Product",
        part_number="TP-001",
        evaluator_id=regular_user.id,
        evaluation_reason="Testing",
        status=EvaluationStatus.DRAFT.value,
        start_date=start_date,
        expected_end_date=expected_end_date,
        process_step="M001",
    )
    session.add(evaluation)
    session.commit()

    # Retrieve the evaluation from the database
    retrieved_evaluation = (
        session.query(Evaluation)
        .filter_by(evaluation_number=evaluation.evaluation_number)
        .first()
    )

    assert retrieved_evaluation is not None
    assert retrieved_evaluation.evaluation_number == evaluation.evaluation_number
    assert retrieved_evaluation.evaluation_type == EvaluationType.NEW_PRODUCT.value
    assert retrieved_evaluation.product_name == "Test Product"
    assert retrieved_evaluation.part_number == "TP-001"
    assert retrieved_evaluation.evaluation_reason == "Testing"
    assert retrieved_evaluation.status == EvaluationStatus.DRAFT.value
    assert retrieved_evaluation.start_date == start_date
    assert retrieved_evaluation.expected_end_date == expected_end_date
    assert retrieved_evaluation.process_step == "M001"
    assert retrieved_evaluation.evaluator_id == regular_user.id


def test_evaluation_status_validation(regular_user):
    """Test that evaluation status is validated correctly."""
    # Valid status
    evaluation = Evaluation(
        evaluation_number="EV-20250101-002",
        evaluation_type=EvaluationType.NEW_PRODUCT.value,
        product_name="Status Test",
        part_number="ST-001",
        evaluator_id=regular_user.id,
        status=EvaluationStatus.IN_PROGRESS.value,
        start_date=datetime.now().date(),
    )
    assert evaluation.status == EvaluationStatus.IN_PROGRESS.value

    # Test setting different status
    evaluation.status = EvaluationStatus.COMPLETED.value
    assert evaluation.status == EvaluationStatus.COMPLETED.value


def test_evaluation_type_validation(regular_user):
    """Test that evaluation type is validated correctly."""
    # Valid type
    evaluation = Evaluation(
        evaluation_number="EV-20250101-004",
        evaluation_type=EvaluationType.MASS_PRODUCTION.value,
        product_name="Type Test",
        part_number="TT-001",
        evaluator_id=regular_user.id,
        status=EvaluationStatus.DRAFT.value,
        start_date=datetime.now().date(),
    )
    assert evaluation.evaluation_type == EvaluationType.MASS_PRODUCTION.value

    # Test setting different type
    evaluation.evaluation_type = EvaluationType.NEW_PRODUCT.value
    assert evaluation.evaluation_type == EvaluationType.NEW_PRODUCT.value


def test_evaluation_to_dict(session, regular_user):
    """Test the to_dict method of the Evaluation model."""
    evaluation = create_test_evaluation(session, regular_user.id)

    evaluation_dict = evaluation.to_dict()

    assert evaluation_dict["evaluation_number"] == evaluation.evaluation_number
    assert evaluation_dict["evaluation_type"] == evaluation.evaluation_type
    assert evaluation_dict["product_name"] == evaluation.product_name
    assert evaluation_dict["part_number"] == evaluation.part_number
    assert evaluation_dict["evaluation_reason"] == evaluation.evaluation_reason
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

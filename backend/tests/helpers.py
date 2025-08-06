"""Helper functions for testing."""

import json
from datetime import datetime, timedelta

from app.models.evaluation import Evaluation, EvaluationStatus, EvaluationType


def create_test_evaluation(session, user_id, **kwargs):
    """Create a test evaluation with default values.

    Args:
        session: SQLAlchemy session
        user_id: ID of the user who created the evaluation
        **kwargs: Override default values

    Returns:
        Evaluation: The created evaluation

    """
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    defaults = {
        "evaluation_number": f"EV-{datetime.now().strftime('%Y%m%d')}-{unique_id}",
        "evaluation_type": EvaluationType.NEW_PRODUCT.value,
        "product_name": "Test Product",
        "part_number": "TP-001",
        "evaluation_reason": "Testing",
        "status": EvaluationStatus.DRAFT.value,
        "start_date": datetime.now().date(),
        "expected_end_date": (datetime.now() + timedelta(days=30)).date(),
        "process_step": "M001",
        "evaluator_id": user_id,
    }

    # Override defaults with kwargs
    for key, value in kwargs.items():
        defaults[key] = value

    evaluation = Evaluation(**defaults)
    session.add(evaluation)
    session.commit()

    return evaluation


def json_response(response):
    """Parse JSON response.

    Args:
        response: Flask test client response

    Returns:
        dict: Parsed JSON response

    """
    return json.loads(response.data.decode("utf-8"))

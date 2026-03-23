"""Unit tests for evaluation API persistence."""

from app.models.evaluation import Evaluation
from tests.helpers import create_test_evaluation, json_response


def test_create_evaluation_persists_pgm_test_time(client, session):
    """POST /api/evaluations should store and return pgm_test_time."""
    response = client.post(
        "/api/evaluations",
        json={
            "evaluation_type": "new_product",
            "product_name": "API Test Product",
            "part_number": "API-001",
            "start_date": "2026-03-23",
            "process_step": "M031",
            "status": "draft",
            "pgm_version": "v1.2.3",
            "pgm_test_time": "90 min",
        },
    )

    body = json_response(response)

    assert response.status_code == 201
    assert body["data"]["evaluation"]["pgm_test_time"] == "90 min"

    created = session.query(Evaluation).get(body["data"]["evaluation"]["id"])
    assert created is not None
    assert created.pgm_version == "v1.2.3"
    assert created.pgm_test_time == "90 min"


def test_update_evaluation_persists_pgm_test_time(client, session):
    """PUT /api/evaluations/<id> should update and return pgm_test_time."""
    evaluation = create_test_evaluation(session, pgm_version="old-version")

    response = client.put(
        f"/api/evaluations/{evaluation.id}",
        json={
            "pgm_version": "new-version",
            "pgm_test_time": "120 min",
        },
    )

    body = json_response(response)

    assert response.status_code == 200
    assert body["data"]["evaluation"]["pgm_version"] == "new-version"
    assert body["data"]["evaluation"]["pgm_test_time"] == "120 min"

    session.refresh(evaluation)
    assert evaluation.pgm_version == "new-version"
    assert evaluation.pgm_test_time == "120 min"

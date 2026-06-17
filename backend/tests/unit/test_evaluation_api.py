"""Unit tests for evaluation API persistence."""

from datetime import date, timedelta

from app.models.evaluation import (
    Evaluation,
    EvaluationNestedProcess,
    EvaluationProcessStep,
    EvaluationStepFailure,
)
from app.utils.timezone import utcnow
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
    assert created.status == "in_progress"


def test_create_evaluation_rejects_unsupported_status(client):
    """POST /api/evaluations should reject removed workflow statuses."""
    response = client.post(
        "/api/evaluations",
        json={
            "evaluation_type": "new_product",
            "product_name": "Invalid Status Product",
            "part_number": "API-STATUS",
            "start_date": "2026-03-23",
            "process_step": "M031",
            "status": "draft",
        },
    )

    body = json_response(response)

    assert response.status_code == 400
    assert body["success"] is False


def test_create_mass_production_evaluation_accepts_pcb_reason(client, session):
    """Mass production evaluations should persist the PCB reason option."""
    response = client.post(
        "/api/evaluations",
        json={
            "evaluation_type": "mass_production",
            "product_name": "PCB Product",
            "part_number": "PCB-001",
            "start_date": "2026-03-23",
            "process_step": "M031",
            "evaluation_reason": "pcb",
        },
    )
    body = json_response(response)

    assert response.status_code == 201
    assert body["data"]["evaluation"]["evaluation_reason"] == "pcb"

    created = session.query(Evaluation).get(body["data"]["evaluation"]["id"])
    assert created.evaluation_reason == "pcb"


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


def test_nested_process_results_are_sanitized_and_persisted(client, session):
    """Nested process results should persist independently for each process."""
    evaluation = create_test_evaluation(session)
    payload = {
        "processes": [
            {
                "key": "proc-aging",
                "name": "Aging Process",
                "order_index": 1,
                "result_html": (
                    "<p><strong>Passed</strong></p>"
                    '<table><colgroup><col width="120"><col width="240"></colgroup>'
                    '<tbody><tr><th>Item</th><th onclick="bad()">Value</th></tr>'
                    "<tr><td>PPM</td><td>0</td></tr></tbody></table>"
                    "<script>alert('bad')</script>"
                ),
                "lots": [
                    {
                        "client_id": "aging-lot",
                        "temp_id": "aging-lot",
                        "lot_number": "LOT-AGING",
                        "quantity": 10,
                    }
                ],
                "steps": [
                    {
                        "order_index": 1,
                        "step_code": "M100",
                        "step_label": "Aging",
                        "lot_refs": ["aging-lot"],
                        "results_applicable": False,
                    }
                ],
            },
            {
                "key": "proc-li",
                "name": "LI Process",
                "order_index": 2,
                "result_html": "<p><em>Review required</em></p>",
                "lots": [
                    {
                        "client_id": "li-lot",
                        "temp_id": "li-lot",
                        "lot_number": "LOT-LI",
                        "quantity": 5,
                    }
                ],
                "steps": [
                    {
                        "order_index": 1,
                        "step_code": "M130",
                        "step_label": "LI",
                        "lot_refs": ["li-lot"],
                        "results_applicable": True,
                        "total_units": 5,
                        "fail_units": 0,
                        "failures": [],
                    }
                ],
            },
        ]
    }

    save_response = client.post(
        f"/api/evaluations/{evaluation.id}/processes/nested",
        json=payload,
    )
    assert save_response.status_code == 200

    stored = (
        session.query(EvaluationNestedProcess)
        .filter_by(evaluation_id=evaluation.id)
        .order_by(EvaluationNestedProcess.order_index)
        .all()
    )
    assert [process.process_key for process in stored] == ["proc-aging", "proc-li"]
    assert "<table>" in stored[0].result_html
    assert '<col width="120"><col width="240">' in stored[0].result_html
    assert "onclick" not in stored[0].result_html
    assert "script" not in stored[0].result_html
    assert "alert" not in stored[0].result_html

    get_response = client.get(f"/api/evaluations/{evaluation.id}/processes/nested")
    body = json_response(get_response)

    assert get_response.status_code == 200
    processes = body["data"]["payload"]["processes"]
    assert processes[0]["result_html"] == stored[0].result_html
    assert processes[1]["result_html"] == "<p><em>Review required</em></p>"


def test_complete_status_uses_user_provided_end_date(client, session):
    """Completing an evaluation should keep the user-provided end date."""
    evaluation = create_test_evaluation(
        session, actual_end_date=None, status="in_progress"
    )

    response = client.put(
        f"/api/evaluations/{evaluation.id}/status",
        json={
            "status": "completed",
            "end_date": "2026-03-20",
        },
    )

    body = json_response(response)

    assert response.status_code == 200
    assert body["data"]["evaluation"]["actual_end_date"] == "2026-03-20"

    session.refresh(evaluation)
    assert evaluation.actual_end_date == date(2026, 3, 20)


def test_complete_status_preserves_existing_end_date_when_not_provided(client, session):
    """Completing without a new end date should not overwrite the saved one."""
    evaluation = create_test_evaluation(
        session,
        actual_end_date=date(2026, 3, 19),
        status="in_progress",
    )

    response = client.put(
        f"/api/evaluations/{evaluation.id}/status",
        json={"status": "completed"},
    )

    body = json_response(response)

    assert response.status_code == 200
    assert body["data"]["evaluation"]["actual_end_date"] == "2026-03-19"

    session.refresh(evaluation)
    assert evaluation.actual_end_date == date(2026, 3, 19)


def _set_updated_at(session, evaluation, updated_at):
    evaluation.updated_at = updated_at
    session.add(evaluation)
    session.commit()


def _add_failed_step(session, evaluation, fail_units=1):
    step = EvaluationProcessStep(
        evaluation_id=evaluation.id,
        lot_number="LOT-FAIL",
        quantity=10,
        order_index=1,
        step_code="M031",
        results_applicable=True,
        total_units=10,
        pass_units=10 - fail_units,
        fail_units=fail_units,
    )
    session.add(step)
    session.flush()
    session.add(
        EvaluationStepFailure(
            step_id=step.id,
            sequence=1,
            fail_code_text="3379",
            analysis_result="Signal integrity issue",
        )
    )
    session.commit()


def test_evaluation_kpis_returns_global_operational_metrics(client, session):
    """GET /api/evaluations/kpis should aggregate the filtered operational set."""
    today = utcnow().date()
    stale_time = utcnow() - timedelta(hours=49)
    previous_month = utcnow().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    ) - timedelta(days=1)

    active_old = create_test_evaluation(
        session,
        evaluation_number="EV-KPI-OLD",
        product_name="Console SSD",
        status="in_progress",
        start_date=today - timedelta(days=12),
    )
    _set_updated_at(session, active_old, stale_time)
    _add_failed_step(session, active_old, fail_units=2)

    active_fresh = create_test_evaluation(
        session,
        evaluation_number="EV-KPI-FRESH",
        product_name="Console SSD",
        status="in_progress",
        start_date=today - timedelta(days=4),
    )
    _set_updated_at(session, active_fresh, utcnow())

    create_test_evaluation(
        session,
        evaluation_number="EV-KPI-COMPLETE",
        product_name="Console SSD",
        status="completed",
        start_date=today - timedelta(days=8),
        actual_end_date=today,
    )

    create_test_evaluation(
        session,
        evaluation_number="EV-KPI-PREVIOUS-MONTH",
        product_name="Console SSD",
        status="cancelled",
        start_date=today,
        created_at=previous_month,
    )

    create_test_evaluation(
        session,
        evaluation_number="EV-KPI-OTHER",
        product_name="Other Product",
        status="in_progress",
        start_date=today - timedelta(days=20),
    )

    response = client.get("/api/evaluations/kpis?product=Console")
    body = json_response(response)

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"] == {
        "open_evaluations": 2,
        "stale_open_evaluations": 1,
        "open_over_10d": 1,
        "median_open_age_days": 8.0,
        "created_this_month": 3,
        "total_evaluations": 4,
        "completed_this_month": 1,
    }


def test_evaluation_list_operational_view_all_active(client, session):
    """The all_active operational view should return only active evaluations."""
    create_test_evaluation(
        session,
        evaluation_number="EV-ACTIVE-1",
        product_name="Active View Product",
        status="in_progress",
    )
    create_test_evaluation(
        session,
        evaluation_number="EV-ACTIVE-2",
        product_name="Active View Product",
        status="cancelled",
    )
    create_test_evaluation(
        session,
        evaluation_number="EV-ACTIVE-3",
        product_name="Active View Product",
        status="completed",
    )

    response = client.get(
        "/api/evaluations?operational_view=all_active&product=Active%20View&per_page=20"
    )
    body = json_response(response)

    numbers = {row["evaluation_number"] for row in body["data"]["evaluations"]}
    assert response.status_code == 200
    assert numbers == {"EV-ACTIVE-1"}


def test_evaluation_list_operational_view_no_update_48h(client, session):
    """The no_update_48h view should return stale active evaluations only."""
    stale = create_test_evaluation(
        session,
        evaluation_number="EV-STALE",
        product_name="Stale View Product",
        status="in_progress",
        start_date=utcnow().date(),
    )
    _set_updated_at(session, stale, utcnow() - timedelta(hours=49))
    fresh = create_test_evaluation(
        session,
        evaluation_number="EV-FRESH",
        product_name="Stale View Product",
        status="in_progress",
        start_date=utcnow().date(),
    )
    _set_updated_at(session, fresh, utcnow())
    completed = create_test_evaluation(
        session,
        evaluation_number="EV-STALE-COMPLETE",
        product_name="Stale View Product",
        status="completed",
        start_date=utcnow().date(),
    )
    _set_updated_at(session, completed, utcnow() - timedelta(hours=72))

    response = client.get(
        "/api/evaluations?operational_view=no_update_48h&product=Stale%20View&per_page=20"
    )
    body = json_response(response)

    assert response.status_code == 200
    numbers = {row["evaluation_number"] for row in body["data"]["evaluations"]}
    assert numbers == {"EV-STALE"}


def test_evaluation_list_operational_view_open_over_10d(client, session):
    """The open_over_10d view should return active evaluations older than 10 days."""
    today = utcnow().date()
    create_test_evaluation(
        session,
        evaluation_number="EV-OLD",
        product_name="Old View Product",
        status="in_progress",
        start_date=today - timedelta(days=10),
    )
    create_test_evaluation(
        session,
        evaluation_number="EV-YOUNG",
        product_name="Old View Product",
        status="in_progress",
        start_date=today - timedelta(days=9),
    )
    create_test_evaluation(
        session,
        evaluation_number="EV-OLD-COMPLETE",
        product_name="Old View Product",
        status="completed",
        start_date=today - timedelta(days=20),
    )

    response = client.get(
        "/api/evaluations?operational_view=open_over_10d&product=Old%20View&per_page=20"
    )
    body = json_response(response)

    assert response.status_code == 200
    numbers = {row["evaluation_number"] for row in body["data"]["evaluations"]}
    assert numbers == {"EV-OLD"}


def test_evaluation_list_operational_view_all(client, session):
    """The all operational view should return every filtered evaluation."""
    create_test_evaluation(
        session,
        evaluation_number="EV-ALL-ACTIVE",
        product_name="All View Product",
        status="in_progress",
    )
    create_test_evaluation(
        session,
        evaluation_number="EV-ALL-COMPLETE",
        product_name="All View Product",
        status="completed",
    )
    create_test_evaluation(
        session,
        evaluation_number="EV-ALL-CANCELLED",
        product_name="All View Product",
        status="cancelled",
    )

    response = client.get(
        "/api/evaluations?operational_view=all&product=All%20View&per_page=20"
    )
    body = json_response(response)

    assert response.status_code == 200
    numbers = {row["evaluation_number"] for row in body["data"]["evaluations"]}
    assert numbers == {"EV-ALL-ACTIVE", "EV-ALL-COMPLETE", "EV-ALL-CANCELLED"}

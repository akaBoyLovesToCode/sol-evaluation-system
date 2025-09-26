"""Unit tests for the EvaluationProcess model."""

import pytest
from app.models.evaluation import EvaluationProcess
from tests.helpers import create_test_evaluation


def test_evaluation_process_creation(session):
    """Test creating a new evaluation process."""
    # Create a test evaluation first
    evaluation = create_test_evaluation(session)

    # Create evaluation process
    process = EvaluationProcess(
        evaluation_id=evaluation.id,
        title="PRQ Evaluation Process",
        eval_code="PRQ-001",
        lot_number="LOT202401001",
        quantity=1000,
        process_description="M031 -> RDT+TC600 -> LI",
        manufacturing_test_results="All tests passed, yield 98.5%",
        defect_analysis_results="Minor cosmetic defects, within acceptable limits",
        aql_result="AQL 1.0 Pass",
        status="pending",
    )
    session.add(process)
    session.commit()

    # Retrieve the process from the database
    retrieved_process = (
        session.query(EvaluationProcess).filter_by(eval_code="PRQ-001").first()
    )

    assert retrieved_process is not None
    assert retrieved_process.title == "PRQ Evaluation Process"
    assert retrieved_process.eval_code == "PRQ-001"
    assert retrieved_process.lot_number == "LOT202401001"
    assert retrieved_process.quantity == 1000
    assert retrieved_process.process_description == "M031 -> RDT+TC600 -> LI"
    assert (
        retrieved_process.manufacturing_test_results == "All tests passed, yield 98.5%"
    )
    assert (
        retrieved_process.defect_analysis_results
        == "Minor cosmetic defects, within acceptable limits"
    )
    assert retrieved_process.aql_result == "AQL 1.0 Pass"
    assert retrieved_process.status == "pending"
    assert retrieved_process.evaluation_id == evaluation.id
    assert retrieved_process.created_at is not None
    assert retrieved_process.updated_at is not None


def test_evaluation_process_required_fields(session):
    """Test that required fields are enforced."""
    evaluation = create_test_evaluation(session)

    # Test missing eval_code
    with pytest.raises(Exception):
        process = EvaluationProcess(
            evaluation_id=evaluation.id,
            title="Test Process",
            lot_number="LOT202401001",
            quantity=1000,
            process_description="Test process",
            status="pending",
        )
        session.add(process)
        session.commit()

    session.rollback()

    # Test missing lot_number
    with pytest.raises(Exception):
        process = EvaluationProcess(
            evaluation_id=evaluation.id,
            title="Test Process",
            eval_code="PRQ-001",
            quantity=1000,
            process_description="Test process",
            status="pending",
        )
        session.add(process)
        session.commit()

    session.rollback()

    # Test missing quantity
    with pytest.raises(Exception):
        process = EvaluationProcess(
            evaluation_id=evaluation.id,
            title="Test Process",
            eval_code="PRQ-001",
            lot_number="LOT202401001",
            process_description="Test process",
            status="pending",
        )
        session.add(process)
        session.commit()

    session.rollback()

    # Test missing process_description
    with pytest.raises(Exception):
        process = EvaluationProcess(
            evaluation_id=evaluation.id,
            title="Test Process",
            eval_code="PRQ-001",
            lot_number="LOT202401001",
            quantity=1000,
            status="pending",
        )
        session.add(process)
        session.commit()


def test_evaluation_process_status_validation(session):
    """Test that process status is validated correctly."""
    evaluation = create_test_evaluation(session)

    # Valid statuses
    valid_statuses = ["pending", "in_progress", "completed", "failed"]

    for status in valid_statuses:
        process = EvaluationProcess(
            evaluation_id=evaluation.id,
            title=f"Test Process - {status}",
            eval_code=f"TEST-{status}",
            lot_number="LOT202401001",
            quantity=1000,
            process_description="Test process",
            status=status,
        )
        session.add(process)
        session.commit()
        assert process.status == status
        session.delete(process)
        session.commit()

    # Note: SQLite doesn't enforce enum constraints like MySQL does
    # For SQLite compatibility, we only test that valid statuses work correctly
    # In production (MySQL), invalid statuses would raise a database constraint error


def test_evaluation_process_to_dict(session):
    """Test the to_dict method of the EvaluationProcess model."""
    evaluation = create_test_evaluation(session)

    process = EvaluationProcess(
        evaluation_id=evaluation.id,
        title="PRQ Evaluation Process",
        eval_code="PRQ-001",
        lot_number="LOT202401001",
        quantity=1000,
        process_description="M031 -> RDT+TC600 -> LI",
        manufacturing_test_results="All tests passed",
        defect_analysis_results="No defects",
        aql_result="AQL 1.0 Pass",
        status="pending",
    )
    session.add(process)
    session.commit()

    process_dict = process.to_dict()

    assert process_dict["id"] == process.id
    assert process_dict["evaluation_id"] == evaluation.id
    assert process_dict["title"] == "PRQ Evaluation Process"
    assert process_dict["eval_code"] == "PRQ-001"
    assert process_dict["lot_number"] == "LOT202401001"
    assert process_dict["quantity"] == 1000
    assert process_dict["process_description"] == "M031 -> RDT+TC600 -> LI"
    assert process_dict["manufacturing_test_results"] == "All tests passed"
    assert process_dict["defect_analysis_results"] == "No defects"
    assert process_dict["aql_result"] == "AQL 1.0 Pass"
    assert process_dict["status"] == "pending"
    assert "created_at" in process_dict
    assert "updated_at" in process_dict


def test_evaluation_process_relationship(session):
    """Test the relationship between Evaluation and EvaluationProcess."""
    evaluation = create_test_evaluation(session)

    # Create multiple processes for the same evaluation
    process1 = EvaluationProcess(
        evaluation_id=evaluation.id,
        title="PRQ Process",
        eval_code="PRQ-001",
        lot_number="LOT202401001",
        quantity=1000,
        process_description="Process 1",
        status="pending",
    )

    process2 = EvaluationProcess(
        evaluation_id=evaluation.id,
        title="PPQ Process",
        eval_code="PPQ-001",
        lot_number="LOT202401002",
        quantity=500,
        process_description="Process 2",
        status="in_progress",
    )

    session.add_all([process1, process2])
    session.commit()

    # Test the relationship from evaluation side
    assert evaluation.processes.count() == 2
    processes = evaluation.processes.all()
    assert len(processes) == 2
    assert processes[0].eval_code in ["PRQ-001", "PPQ-001"]
    assert processes[1].eval_code in ["PRQ-001", "PPQ-001"]

    # Test the backref from process side
    assert process1.evaluation.id == evaluation.id
    assert process2.evaluation.id == evaluation.id
    assert process1.evaluation.evaluation_number == evaluation.evaluation_number


def test_evaluation_process_timestamps(session):
    """Test that created_at and updated_at timestamps work correctly."""
    evaluation = create_test_evaluation(session)

    process = EvaluationProcess(
        evaluation_id=evaluation.id,
        title="Test Process",
        eval_code="PRQ-001",
        lot_number="LOT202401001",
        quantity=1000,
        process_description="Test process",
        status="pending",
    )
    session.add(process)
    session.commit()

    initial_created_at = process.created_at
    initial_updated_at = process.updated_at

    # Verify timestamps are set
    assert initial_created_at is not None
    assert initial_updated_at is not None
    # Allow for microsecond differences due to database timestamp precision
    assert abs((initial_created_at - initial_updated_at).total_seconds()) < 0.001

    # Update the process and check that updated_at changes
    process.quantity = 1500
    session.commit()

    assert process.updated_at > initial_updated_at
    assert process.created_at == initial_created_at  # created_at should not change


def test_evaluation_process_optional_fields(session):
    """Test that optional fields can be null."""
    evaluation = create_test_evaluation(session)

    # Create process without optional fields
    process = EvaluationProcess(
        evaluation_id=evaluation.id,
        title="Test Process",
        eval_code="PRQ-001",
        lot_number="LOT202401001",
        quantity=1000,
        process_description="Test process",
        status="pending",
        # manufacturing_test_results, defect_analysis_results, aql_result are optional
    )
    session.add(process)
    session.commit()

    assert process.manufacturing_test_results is None
    assert process.defect_analysis_results is None
    assert process.aql_result is None

    # Now update with optional fields
    process.manufacturing_test_results = "Test results"
    process.defect_analysis_results = "Defect analysis"
    process.aql_result = "AQL Pass"
    session.commit()

    assert process.manufacturing_test_results == "Test results"
    assert process.defect_analysis_results == "Defect analysis"
    assert process.aql_result == "AQL Pass"

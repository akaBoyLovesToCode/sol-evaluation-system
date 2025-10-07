from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any

from app import db


class EvaluationStatus(Enum):
    """Evaluation status enumeration."""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    PENDING_PART_APPROVAL = "pending_part_approval"
    PENDING_GROUP_APPROVAL = "pending_group_approval"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class EvaluationType(Enum):
    """Evaluation type enumeration."""

    NEW_PRODUCT = "new_product"
    MASS_PRODUCTION = "mass_production"


class Evaluation(db.Model):
    """Main evaluation model for solution evaluations.

    Supports two types of evaluations:
    1. New Solution: DOE, PPQ, PRQ (parallel) -> Part Leader -> Group Leader approval
    2. Mass Production: Production Test -> AQL -> Pass (no approval needed)
    """

    __tablename__ = "evaluations"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Evaluation identification
    evaluation_number = db.Column(
        db.String(50), unique=True, nullable=False, index=True
    )
    evaluation_type = db.Column(
        db.Enum("new_product", "mass_production", name="evaluation_types"),
        nullable=False,
    )

    # Product information
    product_name = db.Column(db.String(100), nullable=False)
    part_number = db.Column(db.String(50), nullable=False)

    # Evaluation details
    evaluation_reason = db.Column(db.Text)
    remarks = db.Column(db.Text)

    # Status and workflow
    status = db.Column(
        db.Enum(
            "draft",
            "in_progress",
            "pending_part_approval",
            "pending_group_approval",
            "completed",
            "paused",
            "cancelled",
            "rejected",
            name="evaluation_status",
        ),
        nullable=False,
        default="draft",
    )

    # Dates
    start_date = db.Column(db.Date, nullable=False)
    actual_end_date = db.Column(db.Date)  # Renamed from completion_date

    # Charger assignments (free text; users removed)
    scs_charger_name = db.Column(db.String(100))
    head_office_charger_name = db.Column(db.String(100))

    # Process information
    process_step = db.Column(
        db.String(20)
    )  # New field for process step identifier (e.g., M031)

    # Technical specifications
    pgm_version = db.Column(db.String(100))  # PGM version
    capacity = db.Column(db.String(100))  # Capacity
    interface_type = db.Column(db.String(100))  # Interface type
    form_factor = db.Column(db.String(100))  # Form factor

    # User relationships removed (auth-less mode)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    details = db.relationship(
        "EvaluationDetail",
        backref="evaluation",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    results = db.relationship(
        "EvaluationResult",
        backref="evaluation",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    processes = db.relationship(
        "EvaluationProcess",
        backref="evaluation",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    nested_process_steps = db.relationship(
        "EvaluationProcessStep",
        backref="evaluation",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    process_raw_records = db.relationship(
        "EvaluationProcessRaw",
        backref="evaluation",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    operation_logs = db.relationship(
        "OperationLog",
        primaryjoin="and_(OperationLog.target_type=='evaluation', "
        "OperationLog.target_id==Evaluation.id)",
        foreign_keys="[OperationLog.target_id]",
        backref=db.backref("evaluation", uselist=False),
        lazy="dynamic",
        viewonly=True,
    )
    # User relationships removed in simplified mode

    def __init__(
        self,
        evaluation_number: str,
        evaluation_type: str,
        product_name: str,
        part_number: str,
        start_date: date,
        **kwargs: Any,
    ) -> None:
        """Initialize evaluation with required fields.

        Args:
            evaluation_number: Unique evaluation identifier.
            evaluation_type: Type of evaluation ('new_product' or 'mass_production').
            product_name: Product name.
            part_number: Product part number.
            start_date: Evaluation start date.
            **kwargs: Additional optional fields.

        """
        self.evaluation_number = evaluation_number
        self.evaluation_type = evaluation_type
        self.product_name = product_name
        self.part_number = part_number
        self.start_date = start_date

        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def can_be_approved_by(self, user: Any) -> bool:
        """Check if user can approve this evaluation.

        Args:
            user: User object to check.

        Returns:
            True if user can approve, False otherwise.

        """
        if self.evaluation_type == "mass_production":
            return False  # Mass production evaluations don't need approval

        # Approvals eliminated; keep statuses reserved but no role checks
        return False

        return False

    def approve(self, approver_id: int, approval_level: str) -> None:
        """Approve evaluation at specified level.

        Args:
            approver_id: ID of the approver.
            approval_level: 'part' or 'group'.

        """
        # No-op (approvals removed). Kept for backward compatibility.
        return

    def reject(self) -> None:
        """Reject the evaluation."""
        self.status = "rejected"

    def complete(self) -> None:
        """Mark evaluation as completed (for mass production)."""
        self.status = "completed"
        self.actual_end_date = datetime.utcnow().date()

    def pause(self) -> None:
        """Pause the evaluation."""
        self.status = "paused"

    def cancel(self) -> None:
        """Cancel the evaluation."""
        self.status = "cancelled"

    def resume(self) -> None:
        """Resume paused evaluation."""
        if self.status == "paused":
            self.status = "in_progress"

    def get_next_approver_role(self) -> str | None:
        """Get the role of next required approver.

        Returns:
            Role name or None if no approval needed.

        """
        if self.evaluation_type == "mass_production":
            return None

        # Reserved statuses retained, but no approver required
        if self.status in [
            "pending_part_approval",
            "pending_group_approval",
        ]:
            return None

        return None

    def to_dict(self, include_details: bool = False) -> dict[str, Any]:
        """Convert evaluation to dictionary.

        Args:
            include_details: Whether to include related details and results.

        Returns:
            Evaluation data dictionary.

        """
        data = {
            "id": self.id,
            "evaluation_number": self.evaluation_number,
            "evaluation_type": self.evaluation_type,
            "product_name": self.product_name,
            "part_number": self.part_number,
            "evaluation_reason": self.evaluation_reason,
            "remarks": self.remarks,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "actual_end_date": self.actual_end_date.isoformat()
            if self.actual_end_date
            else None,
            "process_step": self.process_step,
            "pgm_version": self.pgm_version,
            "capacity": self.capacity,
            "interface_type": self.interface_type,
            "form_factor": self.form_factor,
            "scs_charger_name": self.scs_charger_name,
            "head_office_charger_name": self.head_office_charger_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_details:
            data["details"] = [detail.to_dict() for detail in self.details]
            data["results"] = [result.to_dict() for result in self.results]
            data["processes"] = [process.to_dict() for process in self.processes]

        return data

    def __repr__(self) -> str:
        return f"<Evaluation {self.evaluation_number}>"


class EvaluationDetail(db.Model):
    """Detailed information for specific evaluation types (PGM, Material, etc.)."""

    __tablename__ = "evaluation_details"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key
    evaluation_id = db.Column(
        db.Integer, db.ForeignKey("evaluations.id"), nullable=False
    )

    # Detail type and information
    detail_type = db.Column(
        db.Enum("pgm", "material", "equipment", name="detail_types"), nullable=False
    )

    # PGM specific fields
    pgm_version_before = db.Column(db.String(50))
    pgm_version_after = db.Column(db.String(50))

    # Material specific fields
    material_name = db.Column(db.String(100))
    material_number = db.Column(db.String(50))

    # Equipment specific fields
    equipment_name = db.Column(db.String(100))
    equipment_number = db.Column(db.String(50))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert detail to dictionary.

        Returns:
            Detail data dictionary.

        """
        return {
            "id": self.id,
            "evaluation_id": self.evaluation_id,
            "detail_type": self.detail_type,
            "pgm_version_before": self.pgm_version_before,
            "pgm_version_after": self.pgm_version_after,
            "material_name": self.material_name,
            "material_number": self.material_number,
            "equipment_name": self.equipment_name,
            "equipment_number": self.equipment_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<EvaluationDetail {self.detail_type} for Evaluation {self.evaluation_id}>"
        )


class EvaluationResult(db.Model):
    """Test results for evaluations (DOE, PPQ, PRQ, Production Test, AQL)."""

    __tablename__ = "evaluation_results"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key
    evaluation_id = db.Column(
        db.Integer, db.ForeignKey("evaluations.id"), nullable=False
    )

    # Result type and data
    result_type = db.Column(
        db.Enum("doe", "ppq", "prq", "production_test", "aql", name="result_types"),
        nullable=False,
    )
    result_status = db.Column(
        db.Enum("pass", "fail", "pending", name="result_status"),
        nullable=False,
        default="pending",
    )
    result_data = db.Column(db.JSON)  # Store detailed test results as JSON
    test_date = db.Column(db.Date)

    # Comments and notes
    comments = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary.

        Returns:
            Result data dictionary.

        """
        return {
            "id": self.id,
            "evaluation_id": self.evaluation_id,
            "result_type": self.result_type,
            "result_status": self.result_status,
            "result_data": self.result_data,
            "test_date": self.test_date.isoformat() if self.test_date else None,
            "comments": self.comments,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<EvaluationResult {self.result_type} for Evaluation {self.evaluation_id}>"
        )


class EvaluationProcess(db.Model):
    """Multiple evaluation processes for a single evaluation.

    Supports multiple evaluation attempts for:
    1. New product development (PRQ, PPQ, etc.)
    2. Re-evaluation when first attempt fails
    """

    __tablename__ = "evaluation_processes"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key
    evaluation_id = db.Column(
        db.Integer, db.ForeignKey("evaluations.id"), nullable=False
    )

    # Process identification
    title = db.Column(db.String(100), nullable=False, default="")  # Process title
    eval_code = db.Column(db.String(50), nullable=False)  # Evaluation code
    lot_number = db.Column(db.String(50), nullable=False)  # Lot number
    quantity = db.Column(db.Integer, nullable=False)  # Quantity

    # Process information
    process_description = db.Column(db.Text, nullable=False)  # Process flow description
    manufacturing_test_results = db.Column(db.Text)  # Manufacturing test results
    defect_analysis_results = db.Column(db.Text)  # Defect analysis results
    aql_result = db.Column(db.String(100))  # AQL result (optional)

    # Status
    status = db.Column(
        db.Enum("pending", "in_progress", "completed", "failed", name="process_status"),
        nullable=False,
        default="pending",
    )

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert process to dictionary.

        Returns:
            Process data dictionary.

        """
        return {
            "id": self.id,
            "evaluation_id": self.evaluation_id,
            "title": self.title,
            "eval_code": self.eval_code,
            "lot_number": self.lot_number,
            "quantity": self.quantity,
            "process_description": self.process_description,
            "manufacturing_test_results": self.manufacturing_test_results,
            "defect_analysis_results": self.defect_analysis_results,
            "aql_result": self.aql_result,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<EvaluationProcess {self.eval_code} for Evaluation {self.evaluation_id}>"
        )


class EvaluationProcessRaw(db.Model):
    """Stores full JSON submissions from the nested process editor."""

    __tablename__ = "evaluation_processes_raw"

    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(
        db.Integer, db.ForeignKey("evaluations.id"), nullable=False, index=True
    )
    payload = db.Column(db.JSON, nullable=False)
    source = db.Column(db.String(32), nullable=False, default="rc0")

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<EvaluationProcessRaw eval={self.evaluation_id} source={self.source}>"


class EvaluationProcessStep(db.Model):
    """Normalized nested process step information."""

    __tablename__ = "evaluation_process_steps"

    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(
        db.Integer, db.ForeignKey("evaluations.id"), nullable=False, index=True
    )
    lot_number = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    order_index = db.Column(db.Integer, nullable=False, default=1)
    step_code = db.Column(db.String(32), nullable=False)
    step_label = db.Column(db.String(255))
    eval_code = db.Column(db.String(64), nullable=False)
    total_units = db.Column(db.Integer, nullable=False, default=0)
    pass_units = db.Column(db.Integer, nullable=False, default=0)
    fail_units = db.Column(db.Integer, nullable=False, default=0)
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    failures = db.relationship(
        "EvaluationStepFailure",
        backref="step",
        lazy="joined",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<EvaluationProcessStep eval={self.evaluation_id} code={self.step_code} order={self.order_index}>"


class EvaluationStepFailure(db.Model):
    """Failure details captured under each nested process step."""

    __tablename__ = "evaluation_step_failures"

    id = db.Column(db.Integer, primary_key=True)
    step_id = db.Column(
        db.Integer, db.ForeignKey("evaluation_process_steps.id"), nullable=False
    )
    sequence = db.Column(db.Integer, nullable=False, default=1)
    serial_number = db.Column(db.String(100))

    fail_code_id = db.Column(db.Integer, db.ForeignKey("fail_codes.id"))
    fail_code_text = db.Column(db.String(32), nullable=False)
    fail_code_name_snapshot = db.Column(db.String(255))
    analysis_result = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<EvaluationStepFailure step={self.step_id} code={self.fail_code_text} seq={self.sequence}>"


class FailCode(db.Model):
    """Dictionary of known fail codes for evaluation analysis."""

    __tablename__ = "fail_codes"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), nullable=False, unique=True, index=True)
    short_name = db.Column(db.String(255))
    description = db.Column(db.Text)
    is_provisional = db.Column(db.Boolean, nullable=False, default=False)
    source = db.Column(db.String(64))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        status = "provisional" if self.is_provisional else "official"
        return f"<FailCode {self.code} ({status})>"

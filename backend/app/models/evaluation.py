from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any

from sqlalchemy import func

from app import db
from app.utils.timezone import iso_date, iso_local, utcnow


class EvaluationStatus(Enum):
    """Evaluation status enumeration."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EvaluationType(Enum):
    """Evaluation type enumeration."""

    NEW_PRODUCT = "new_product"
    MASS_PRODUCTION = "mass_production"


nand_evaluation_applied_products = db.Table(
    "nand_evaluation_applied_products",
    db.Column(
        "nand_evaluation_id",
        db.Integer,
        db.ForeignKey("nand_evaluations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "applied_product_id",
        db.Integer,
        db.ForeignKey("nand_applied_products.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

nand_evaluation_grades = db.Table(
    "nand_evaluation_grades",
    db.Column(
        "nand_evaluation_id",
        db.Integer,
        db.ForeignKey("nand_evaluations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "grade_id",
        db.Integer,
        db.ForeignKey("nand_grades.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class NandProduct(db.Model):
    """NAND DR and product row shown on the NAND timeline."""

    __tablename__ = "nand_products"
    __table_args__ = (
        db.UniqueConstraint(
            "dr_generation",
            "product_code",
            name="uq_nand_product_dr_product",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    dr_generation = db.Column(db.String(20), nullable=False, index=True)
    product_code = db.Column(db.String(20), nullable=False, index=True)
    display_order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
    )

    def to_dict(self, tz=None) -> dict[str, Any]:
        return {
            "id": self.id,
            "dr_generation": self.dr_generation,
            "product_code": self.product_code,
            "display_order": self.display_order,
            "is_active": self.is_active,
            "created_at": iso_local(self.created_at, tz),
            "updated_at": iso_local(self.updated_at, tz),
        }

    def __repr__(self) -> str:
        return f"<NandProduct {self.dr_generation}_{self.product_code}>"


class NandAppliedProduct(db.Model):
    """Applied product model associated with a NAND evaluation."""

    __tablename__ = "nand_applied_products"

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False, unique=True, index=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
    )

    def to_dict(self, tz=None) -> dict[str, Any]:
        return {
            "id": self.id,
            "model_name": self.model_name,
            "created_at": iso_local(self.created_at, tz),
            "updated_at": iso_local(self.updated_at, tz),
        }

    def __repr__(self) -> str:
        return f"<NandAppliedProduct {self.model_name}>"


class NandGrade(db.Model):
    """NAND grade or approval level associated with a NAND evaluation."""

    __tablename__ = "nand_grades"

    id = db.Column(db.Integer, primary_key=True)
    grade_code = db.Column(db.String(50), nullable=False, unique=True, index=True)
    grade_family = db.Column(db.String(50), nullable=False, default="unknown")

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
    )

    def to_dict(self, tz=None) -> dict[str, Any]:
        return {
            "id": self.id,
            "grade_code": self.grade_code,
            "grade_family": self.grade_family,
            "created_at": iso_local(self.created_at, tz),
            "updated_at": iso_local(self.updated_at, tz),
        }

    def __repr__(self) -> str:
        return f"<NandGrade {self.grade_code}>"


class NandEvaluation(db.Model):
    """NAND-specific extension for one evaluation timeline node."""

    __tablename__ = "nand_evaluations"

    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(
        db.Integer,
        db.ForeignKey("evaluations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    nand_product_id = db.Column(
        db.Integer, db.ForeignKey("nand_products.id"), nullable=False, index=True
    )
    milestone_date = db.Column(db.Date, nullable=False, index=True)
    milestone_status = db.Column(
        db.Enum(
            "approved",
            "current_month_plan",
            "follow_up_plan",
            name="nand_milestone_status",
        ),
        nullable=False,
    )
    evaluation_item = db.Column(db.String(100), nullable=False)
    fab_line = db.Column(db.String(50), nullable=False)
    remark = db.Column(db.Text)
    remark_top = db.Column(db.Text)
    remark_bottom = db.Column(db.Text)
    sort_order = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
    )

    nand_product = db.relationship(
        "NandProduct",
        backref=db.backref("nand_evaluations", lazy="dynamic"),
    )
    applied_products = db.relationship(
        "NandAppliedProduct",
        secondary=nand_evaluation_applied_products,
        lazy="joined",
    )
    grades = db.relationship(
        "NandGrade",
        secondary=nand_evaluation_grades,
        lazy="joined",
    )
    source_relations = db.relationship(
        "NandTimelineRelation",
        foreign_keys="NandTimelineRelation.from_nand_evaluation_id",
        back_populates="from_nand_evaluation",
        cascade="all, delete-orphan",
    )
    destination_relations = db.relationship(
        "NandTimelineRelation",
        foreign_keys="NandTimelineRelation.to_nand_evaluation_id",
        back_populates="to_nand_evaluation",
        cascade="all, delete-orphan",
    )

    def to_dict(self, tz=None) -> dict[str, Any]:
        return {
            "id": self.id,
            "evaluation_id": self.evaluation_id,
            "nand_product_id": self.nand_product_id,
            "dr_generation": self.nand_product.dr_generation
            if self.nand_product
            else None,
            "product_code": self.nand_product.product_code
            if self.nand_product
            else None,
            "product": self.nand_product.to_dict(tz=tz) if self.nand_product else None,
            "milestone_date": iso_date(self.milestone_date, tz),
            "milestone_status": self.milestone_status,
            "evaluation_item": self.evaluation_item,
            "fab_line": self.fab_line,
            "applied_products": [
                product.model_name
                for product in sorted(self.applied_products, key=lambda p: p.model_name)
            ],
            "grades": [
                grade.grade_code
                for grade in sorted(self.grades, key=lambda g: g.grade_code)
            ],
            "remark": self.remark,
            "remark_top": self.remark_top,
            "remark_bottom": self.remark_bottom,
            "sort_order": self.sort_order,
            "relations_from": [
                relation.to_dict(tz=tz)
                for relation in sorted(
                    self.source_relations, key=lambda r: r.display_order
                )
            ],
            "created_at": iso_local(self.created_at, tz),
            "updated_at": iso_local(self.updated_at, tz),
        }

    def __repr__(self) -> str:
        return f"<NandEvaluation eval={self.evaluation_id}>"


class NandTimelineRelation(db.Model):
    """Visual relationship between two NAND timeline nodes."""

    __tablename__ = "nand_timeline_relations"

    id = db.Column(db.Integer, primary_key=True)
    from_nand_evaluation_id = db.Column(
        db.Integer,
        db.ForeignKey("nand_evaluations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    to_nand_evaluation_id = db.Column(
        db.Integer,
        db.ForeignKey("nand_evaluations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relation_type = db.Column(db.String(50), nullable=False, default="delay")
    label = db.Column(db.String(100))
    color = db.Column(db.String(20))
    display_order = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
    )

    from_nand_evaluation = db.relationship(
        "NandEvaluation",
        foreign_keys=[from_nand_evaluation_id],
        back_populates="source_relations",
    )
    to_nand_evaluation = db.relationship(
        "NandEvaluation",
        foreign_keys=[to_nand_evaluation_id],
        back_populates="destination_relations",
    )

    def to_dict(self, tz=None) -> dict[str, Any]:
        return {
            "id": self.id,
            "from_nand_evaluation_id": self.from_nand_evaluation_id,
            "to_nand_evaluation_id": self.to_nand_evaluation_id,
            "relation_type": self.relation_type,
            "label": self.label,
            "color": self.color,
            "display_order": self.display_order,
            "created_at": iso_local(self.created_at, tz),
            "updated_at": iso_local(self.updated_at, tz),
        }

    def __repr__(self) -> str:
        return (
            f"<NandTimelineRelation {self.from_nand_evaluation_id}"
            f"->{self.to_nand_evaluation_id}>"
        )


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
    evaluation_name = db.Column(db.String(255))
    evaluation_type = db.Column(
        db.Enum("new_product", "mass_production", name="evaluation_types"),
        nullable=False,
    )

    # Product information
    product_name = db.Column(db.String(100), nullable=False)
    part_number = db.Column(db.String(50), nullable=False)

    # Evaluation details
    evaluation_reason = db.Column(db.Text)
    cancel_reason = db.Column(db.Text)
    remarks = db.Column(db.Text)
    test_process = db.Column(db.Text)  # Test process notes
    v_process = db.Column(db.Text)  # V process notes
    pgm_login_text = db.Column(db.Text)  # PGM login description
    pgm_login_image = db.Column(db.Text)  # PGM login image (base64 or data URL)

    # Status and workflow
    status = db.Column(
        db.Enum(
            "in_progress",
            "completed",
            "cancelled",
            name="evaluation_status",
        ),
        nullable=False,
        default="in_progress",
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
    pgm_test_time = db.Column(db.String(100))  # PGM test time
    capacity = db.Column(db.String(100))  # Capacity
    interface_type = db.Column(db.String(100))  # Interface type
    form_factor = db.Column(db.String(100))  # Form factor

    # User relationships removed (auth-less mode)

    # Timestamps
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
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
    nested_process_lots = db.relationship(
        "EvaluationProcessLot",
        backref="evaluation",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    nested_processes = db.relationship(
        "EvaluationNestedProcess",
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
    nand_evaluation = db.relationship(
        "NandEvaluation",
        backref="evaluation",
        uselist=False,
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
        self.status = "cancelled"

    def complete(self) -> None:
        """Mark evaluation as completed (for mass production)."""
        self.status = "completed"
        self.actual_end_date = utcnow().date()

    def pause(self) -> None:
        """Pause the evaluation."""
        self.status = "in_progress"

    def cancel(self) -> None:
        """Cancel the evaluation."""
        self.status = "cancelled"

    def resume(self) -> None:
        """Resume evaluation."""
        if self.status != "completed":
            self.status = "in_progress"

    def get_next_approver_role(self) -> str | None:
        """Get the role of next required approver.

        Returns:
            Role name or None if no approval needed.

        """
        if self.evaluation_type == "mass_production":
            return None

        return None

    def to_dict(self, include_details: bool = False, tz=None) -> dict[str, Any]:
        """Convert evaluation to dictionary.

        Args:
            include_details: Whether to include related details and results.

        Returns:
            Evaluation data dictionary.

        """
        data = {
            "id": self.id,
            "evaluation_number": self.evaluation_number,
            "evaluation_name": self.evaluation_name,
            "evaluation_type": self.evaluation_type,
            "product_name": self.product_name,
            "part_number": self.part_number,
            "evaluation_reason": self.evaluation_reason,
            "cancel_reason": self.cancel_reason,
            "remarks": self.remarks,
            "test_process": self.test_process,
            "v_process": self.v_process,
            "pgm_login_text": self.pgm_login_text,
            "pgm_login_image": self.pgm_login_image,
            "status": self.status,
            "start_date": iso_date(self.start_date, tz),
            "actual_end_date": iso_date(self.actual_end_date, tz),
            "process_step": self.process_step,
            "pgm_version": self.pgm_version,
            "pgm_test_time": self.pgm_test_time,
            "capacity": self.capacity,
            "interface_type": self.interface_type,
            "form_factor": self.form_factor,
            "scs_charger_name": self.scs_charger_name,
            "head_office_charger_name": self.head_office_charger_name,
            "created_at": iso_local(self.created_at, tz),
            "updated_at": iso_local(self.updated_at, tz),
            "nand_info": self.nand_evaluation.to_dict(tz=tz)
            if self.nand_evaluation
            else None,
        }

        if include_details:
            data["details"] = [detail.to_dict(tz=tz) for detail in self.details]
            data["results"] = [result.to_dict(tz=tz) for result in self.results]
            data["processes"] = [process.to_dict(tz=tz) for process in self.processes]

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
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
    )

    def to_dict(self, tz=None) -> dict[str, Any]:
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
            "created_at": iso_local(self.created_at, tz),
            "updated_at": iso_local(self.updated_at, tz),
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
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
    )

    def to_dict(self, tz=None) -> dict[str, Any]:
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
            "test_date": iso_date(self.test_date, tz),
            "comments": self.comments,
            "created_at": iso_local(self.created_at, tz),
            "updated_at": iso_local(self.updated_at, tz),
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
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
    )

    def to_dict(self, tz=None) -> dict[str, Any]:
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
            "created_at": iso_local(self.created_at, tz),
            "updated_at": iso_local(self.updated_at, tz),
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

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<EvaluationProcessRaw eval={self.evaluation_id} source={self.source}>"


class EvaluationNestedProcess(db.Model):
    """Process-level metadata for the nested process editor."""

    __tablename__ = "evaluation_nested_processes"
    __table_args__ = (
        db.UniqueConstraint(
            "evaluation_id",
            "process_key",
            name="uq_evaluation_nested_process_key",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(
        db.Integer, db.ForeignKey("evaluations.id"), nullable=False, index=True
    )
    process_key = db.Column(db.String(64), nullable=False)
    process_name = db.Column(db.String(255), nullable=False)
    order_index = db.Column(db.Integer, nullable=False, default=1)
    result_html = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<EvaluationNestedProcess eval={self.evaluation_id} "
            f"key={self.process_key}>"
        )


class EvaluationProcessLot(db.Model):
    """Lot definitions associated with a nested evaluation process."""

    __tablename__ = "evaluation_process_lots"

    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(
        db.Integer, db.ForeignKey("evaluations.id"), nullable=False, index=True
    )
    lot_number = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    client_id = db.Column(db.String(64))
    process_key = db.Column(db.String(64))
    process_name = db.Column(db.String(255))
    process_order_index = db.Column(db.Integer)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
    )

    lot_assignments = db.relationship(
        "EvaluationStepLot",
        backref="lot",
        lazy="select",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<EvaluationProcessLot eval={self.evaluation_id} lot={self.lot_number}>"


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
    eval_code = db.Column(db.String(64))
    results_applicable = db.Column(db.Boolean, nullable=False, default=True)
    total_units = db.Column(db.Integer)
    total_units_manual = db.Column(db.Boolean, nullable=False, default=False)
    pass_units = db.Column(db.Integer)
    fail_units = db.Column(db.Integer)
    notes = db.Column(db.Text)
    process_key = db.Column(db.String(64))
    process_name = db.Column(db.String(255))
    process_order_index = db.Column(db.Integer)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
    )

    failures = db.relationship(
        "EvaluationStepFailure",
        backref="step",
        lazy="joined",
        cascade="all, delete-orphan",
    )
    lot_assignments = db.relationship(
        "EvaluationStepLot",
        backref="step",
        lazy="joined",
        cascade="all, delete-orphan",
    )
    lots = db.relationship(
        "EvaluationProcessLot",
        secondary="evaluation_step_lots",
        viewonly=True,
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<EvaluationProcessStep eval={self.evaluation_id} code={self.step_code} order={self.order_index}>"


class EvaluationStepLot(db.Model):
    """Association table mapping steps to the lots they reference."""

    __tablename__ = "evaluation_step_lots"

    step_id = db.Column(
        db.Integer,
        db.ForeignKey("evaluation_process_steps.id", ondelete="CASCADE"),
        primary_key=True,
    )
    lot_id = db.Column(
        db.Integer,
        db.ForeignKey("evaluation_process_lots.id", ondelete="CASCADE"),
        primary_key=True,
    )
    quantity_override = db.Column(db.Integer)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<EvaluationStepLot step={self.step_id} lot={self.lot_id}>"


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

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
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

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        status = "provisional" if self.is_provisional else "official"
        return f"<FailCode {self.code} ({status})>"

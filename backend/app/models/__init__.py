"""Database models package for Solution Evaluation System"""

from app import db

from .evaluation import (
    Evaluation,
    EvaluationDetail,
    EvaluationNestedProcess,
    EvaluationProcess,
    EvaluationProcessRaw,
    EvaluationProcessStep,
    EvaluationResult,
    EvaluationStepFailure,
    FailCode,
    NandAppliedProduct,
    NandEvaluation,
    NandGrade,
    NandProduct,
    NandTimelineRelation,
)
from .operation_log import OperationLog
from .system_config import SystemConfig

# Export all models for easy importing
__all__ = [
    "db",
    "Evaluation",
    "EvaluationDetail",
    "EvaluationNestedProcess",
    "EvaluationProcess",
    "EvaluationProcessRaw",
    "EvaluationProcessStep",
    "EvaluationStepFailure",
    "EvaluationResult",
    "FailCode",
    "NandAppliedProduct",
    "NandEvaluation",
    "NandGrade",
    "NandProduct",
    "NandTimelineRelation",
    "OperationLog",
    "SystemConfig",
]

"""Database models package for Solution Evaluation System"""

from app import db

from .evaluation import (
    Evaluation,
    EvaluationDetail,
    EvaluationProcess,
    EvaluationProcessRaw,
    EvaluationProcessStep,
    EvaluationStepFailure,
    EvaluationResult,
    FailCode,
)
from .operation_log import OperationLog
from .system_config import SystemConfig

# Export all models for easy importing
__all__ = [
    "db",
    "Evaluation",
    "EvaluationDetail",
    "EvaluationProcess",
    "EvaluationProcessRaw",
    "EvaluationProcessStep",
    "EvaluationStepFailure",
    "EvaluationResult",
    "FailCode",
    "OperationLog",
    "SystemConfig",
]

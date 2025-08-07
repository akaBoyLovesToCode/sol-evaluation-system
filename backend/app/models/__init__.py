"""Database models package for Solution Evaluation System"""

from app import db

from .evaluation import Evaluation, EvaluationDetail, EvaluationResult
from .message import Message
from .operation_log import OperationLog
from .system_config import SystemConfig
from .user import User

# Export all models for easy importing
__all__ = [
    "db",
    "User",
    "Evaluation",
    "EvaluationDetail",
    "EvaluationResult",
    "Message",
    "OperationLog",
    "SystemConfig",
]

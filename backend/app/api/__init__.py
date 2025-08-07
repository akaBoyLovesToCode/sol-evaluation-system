"""API package for Solution Evaluation System.

Contains all REST API endpoints organized by functionality.
"""

from .auth import auth_bp
from .dashboard import dashboard_bp
from .evaluation import evaluation_bp
from .operation_log import operation_log_bp
from .user import user_bp

# Export all blueprints for easy importing
__all__ = ["auth_bp", "evaluation_bp", "user_bp", "dashboard_bp", "operation_log_bp"]

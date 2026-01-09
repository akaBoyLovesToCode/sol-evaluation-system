from enum import Enum

from sqlalchemy import func

from app import db
from app.utils.timezone import iso_local, utcnow


class OperationType(Enum):
    """Operation type enumeration"""

    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    EXPORT = "export"
    VIEW = "view"


class OperationLog(db.Model):
    """Operation log model for tracking user activities and system changes

    Tracks:
    - User login/logout
    - Evaluation CRUD operations
    - Approval actions
    - Status changes
    - Data exports
    """

    __tablename__ = "operation_logs"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Operation information (no user FK; IP-based attribution)
    operation_type = db.Column(
        db.Enum(
            "login",
            "logout",
            "create",
            "update",
            "delete",
            "approve",
            "reject",
            "export",
            "view",
            name="operation_types",
        ),
        nullable=False,
    )

    # Target information
    target_type = db.Column(
        db.String(50), nullable=False
    )  # 'evaluation', 'user', 'system', etc.
    target_id = db.Column(
        db.Integer
    )  # ID of the target object (nullable for system operations)
    target_description = db.Column(db.String(200))  # Human-readable description

    # Operation details
    operation_description = db.Column(db.Text)  # Detailed description of the operation
    old_data = db.Column(db.JSON)  # Previous state (for updates)
    new_data = db.Column(db.JSON)  # New state (for creates/updates)

    # Request information
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6 address
    user_agent = db.Column(db.String(500))  # Browser/client information
    request_method = db.Column(db.String(10))
    request_path = db.Column(db.String(200))
    query_string = db.Column(db.Text)
    status_code = db.Column(db.Integer)

    # Result and status
    success = db.Column(db.Boolean, default=True, nullable=False)
    error_message = db.Column(db.Text)  # Error details if operation failed

    # Timestamp
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    def __init__(self, operation_type, target_type, **kwargs):
        """Initialize operation log with required fields

        Args:
            operation_type (str): Type of operation
            target_type (str): Type of target object

        """
        self.operation_type = operation_type
        self.target_type = target_type

        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @staticmethod
    def log_login(ip_address=None, user_agent=None, success=True, error_message=None):
        """Log user login attempt

        Args:
            ip_address (str): Client IP address
            user_agent (str): Client user agent
            success (bool): Whether login was successful
            error_message (str): Error message if login failed

        Returns:
            OperationLog: Created log entry

        """
        log = OperationLog(
            operation_type="login",
            target_type="user",
            operation_description="User login attempt",
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
        )

        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def log_logout(ip_address=None):
        """Log user logout

        Args:
            ip_address (str): Client IP address

        Returns:
            OperationLog: Created log entry

        """
        log = OperationLog(
            operation_type="logout",
            target_type="user",
            operation_description="User logout",
            ip_address=ip_address,
        )

        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def log_evaluation_operation(
        operation_type,
        evaluation,
        old_data=None,
        ip_address=None,
        success=True,
        error_message=None,
    ):
        """Log evaluation-related operations

        Args:
            operation_type (str): Type of operation ('create', 'update', 'delete', etc.)
            evaluation (Evaluation): Evaluation object
            old_data (dict): Previous state for updates
            ip_address (str): Client IP address
            success (bool): Whether operation was successful
            error_message (str): Error message if operation failed

        Returns:
            OperationLog: Created log entry

        """
        operation_descriptions = {
            "create": f"Created evaluation {evaluation.evaluation_number}",
            "update": f"Updated evaluation {evaluation.evaluation_number}",
            "delete": f"Deleted evaluation {evaluation.evaluation_number}",
            "approve": f"Approved evaluation {evaluation.evaluation_number}",
            "reject": f"Rejected evaluation {evaluation.evaluation_number}",
            "view": f"Viewed evaluation {evaluation.evaluation_number}",
        }

        log = OperationLog(
            operation_type=operation_type,
            target_type="evaluation",
            target_id=evaluation.id,
            target_description=f"{evaluation.evaluation_number} - {evaluation.product_name}",
            operation_description=operation_descriptions.get(
                operation_type, f"{operation_type} evaluation"
            ),
            old_data=old_data,
            new_data=evaluation.to_dict()
            if operation_type in ["create", "update"]
            else None,
            ip_address=ip_address,
            success=success,
            error_message=error_message,
        )

        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def log_data_export(
        export_type,
        filters=None,
        ip_address=None,
        success=True,
        error_message=None,
    ):
        """Log data export operations

        Args:
            export_type (str): Type of export ('evaluations', 'reports', etc.)
            filters (dict): Export filters applied
            ip_address (str): Client IP address
            success (bool): Whether export was successful
            error_message (str): Error message if export failed

        Returns:
            OperationLog: Created log entry

        """
        log = OperationLog(
            operation_type="export",
            target_type="data",
            operation_description=f"Exported {export_type} data",
            new_data={"export_type": export_type, "filters": filters},
            ip_address=ip_address,
            success=success,
            error_message=error_message,
        )

        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def log_system_operation(
        operation_description,
        operation_data=None,
        ip_address=None,
        success=True,
        error_message=None,
    ):
        """Log system-level operations

        Args:
            operation_description (str): Description of the operation
            operation_data (dict): Additional operation data
            ip_address (str): Client IP address
            success (bool): Whether operation was successful
            error_message (str): Error message if operation failed

        Returns:
            OperationLog: Created log entry

        """
        log = OperationLog(
            operation_type="update",
            target_type="system",
            operation_description=operation_description,
            new_data=operation_data,
            ip_address=ip_address,
            success=success,
            error_message=error_message,
        )

        db.session.add(log)
        db.session.commit()
        return log

    def to_dict(self, tz=None):
        """Convert operation log to dictionary

        Returns:
            dict: Operation log data dictionary

        """
        return {
            "id": self.id,
            "operation_type": self.operation_type,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "target_description": self.target_description,
            "operation_description": self.operation_description,
            "old_data": self.old_data,
            "new_data": self.new_data,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "request_method": self.request_method,
            "request_path": self.request_path,
            "query_string": self.query_string,
            "status_code": self.status_code,
            "success": self.success,
            "error_message": self.error_message,
            "created_at": iso_local(self.created_at, tz),
        }

    def __repr__(self):
        return (
            f"<OperationLog {self.operation_type} on {self.target_type}"
            f"{f' #{self.target_id}' if self.target_id is not None else ''}>"
        )

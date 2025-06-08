from datetime import datetime
from enum import Enum
from app import db


class OperationType(Enum):
    """Operation type enumeration"""
    LOGIN = 'login'
    LOGOUT = 'logout'
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    APPROVE = 'approve'
    REJECT = 'reject'
    EXPORT = 'export'
    VIEW = 'view'

class OperationLog(db.Model):
    """
    Operation log model for tracking user activities and system changes
    
    Tracks:
    - User login/logout
    - Evaluation CRUD operations
    - Approval actions
    - Status changes
    - Data exports
    """
    
    __tablename__ = 'operation_logs'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # User and operation information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    operation_type = db.Column(db.Enum('login', 'logout', 'create', 'update', 'delete', 
                                     'approve', 'reject', 'export', 'view', name='operation_types'), 
                             nullable=False)
    
    # Target information
    target_type = db.Column(db.String(50), nullable=False)  # 'evaluation', 'user', 'system', etc.
    target_id = db.Column(db.Integer)  # ID of the target object (nullable for system operations)
    target_description = db.Column(db.String(200))  # Human-readable description
    
    # Operation details
    operation_description = db.Column(db.Text)  # Detailed description of the operation
    old_data = db.Column(db.JSON)  # Previous state (for updates)
    new_data = db.Column(db.JSON)  # New state (for creates/updates)
    
    # Request information
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6 address
    user_agent = db.Column(db.String(500))  # Browser/client information
    
    # Result and status
    success = db.Column(db.Boolean, default=True, nullable=False)
    error_message = db.Column(db.Text)  # Error details if operation failed
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __init__(self, user_id, operation_type, target_type, **kwargs):
        """
        Initialize operation log with required fields
        
        Args:
            user_id (int): ID of the user performing the operation
            operation_type (str): Type of operation
            target_type (str): Type of target object
        """
        self.user_id = user_id
        self.operation_type = operation_type
        self.target_type = target_type
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @staticmethod
    def log_login(user_id, ip_address=None, user_agent=None, success=True, error_message=None):
        """
        Log user login attempt
        
        Args:
            user_id (int): User ID
            ip_address (str): Client IP address
            user_agent (str): Client user agent
            success (bool): Whether login was successful
            error_message (str): Error message if login failed
        
        Returns:
            OperationLog: Created log entry
        """
        log = OperationLog(
            user_id=user_id,
            operation_type='login',
            target_type='user',
            target_id=user_id,
            operation_description='User login attempt',
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message
        )
        
        db.session.add(log)
        db.session.commit()
        return log
    
    @staticmethod
    def log_logout(user_id, ip_address=None):
        """
        Log user logout
        
        Args:
            user_id (int): User ID
            ip_address (str): Client IP address
        
        Returns:
            OperationLog: Created log entry
        """
        log = OperationLog(
            user_id=user_id,
            operation_type='logout',
            target_type='user',
            target_id=user_id,
            operation_description='User logout',
            ip_address=ip_address
        )
        
        db.session.add(log)
        db.session.commit()
        return log
    
    @staticmethod
    def log_evaluation_operation(user_id, operation_type, evaluation, old_data=None, 
                                ip_address=None, success=True, error_message=None):
        """
        Log evaluation-related operations
        
        Args:
            user_id (int): User ID
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
            'create': f'Created evaluation {evaluation.evaluation_number}',
            'update': f'Updated evaluation {evaluation.evaluation_number}',
            'delete': f'Deleted evaluation {evaluation.evaluation_number}',
            'approve': f'Approved evaluation {evaluation.evaluation_number}',
            'reject': f'Rejected evaluation {evaluation.evaluation_number}',
            'view': f'Viewed evaluation {evaluation.evaluation_number}'
        }
        
        log = OperationLog(
            user_id=user_id,
            operation_type=operation_type,
            target_type='evaluation',
            target_id=evaluation.id,
            target_description=f'{evaluation.evaluation_number} - {evaluation.ssd_product}',
            operation_description=operation_descriptions.get(operation_type, f'{operation_type} evaluation'),
            old_data=old_data,
            new_data=evaluation.to_dict() if operation_type in ['create', 'update'] else None,
            ip_address=ip_address,
            success=success,
            error_message=error_message
        )
        
        db.session.add(log)
        db.session.commit()
        return log
    
    @staticmethod
    def log_data_export(user_id, export_type, filters=None, ip_address=None, 
                       success=True, error_message=None):
        """
        Log data export operations
        
        Args:
            user_id (int): User ID
            export_type (str): Type of export ('evaluations', 'reports', etc.)
            filters (dict): Export filters applied
            ip_address (str): Client IP address
            success (bool): Whether export was successful
            error_message (str): Error message if export failed
        
        Returns:
            OperationLog: Created log entry
        """
        log = OperationLog(
            user_id=user_id,
            operation_type='export',
            target_type='data',
            operation_description=f'Exported {export_type} data',
            new_data={'export_type': export_type, 'filters': filters},
            ip_address=ip_address,
            success=success,
            error_message=error_message
        )
        
        db.session.add(log)
        db.session.commit()
        return log
    
    @staticmethod
    def log_system_operation(user_id, operation_description, operation_data=None, 
                           ip_address=None, success=True, error_message=None):
        """
        Log system-level operations
        
        Args:
            user_id (int): User ID
            operation_description (str): Description of the operation
            operation_data (dict): Additional operation data
            ip_address (str): Client IP address
            success (bool): Whether operation was successful
            error_message (str): Error message if operation failed
        
        Returns:
            OperationLog: Created log entry
        """
        log = OperationLog(
            user_id=user_id,
            operation_type='update',
            target_type='system',
            operation_description=operation_description,
            new_data=operation_data,
            ip_address=ip_address,
            success=success,
            error_message=error_message
        )
        
        db.session.add(log)
        db.session.commit()
        return log
    
    def to_dict(self):
        """
        Convert operation log to dictionary
        
        Returns:
            dict: Operation log data dictionary
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else 'Unknown',
            'operation_type': self.operation_type,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'target_description': self.target_description,
            'operation_description': self.operation_description,
            'old_data': self.old_data,
            'new_data': self.new_data,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'success': self.success,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<OperationLog {self.operation_type} on {self.target_type} by User {self.user_id}>' 
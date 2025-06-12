from datetime import datetime
from enum import Enum
from app import db


class EvaluationStatus(Enum):
    """Evaluation status enumeration"""
    DRAFT = 'draft'
    IN_PROGRESS = 'in_progress'
    PENDING_PART_APPROVAL = 'pending_part_approval'
    PENDING_GROUP_APPROVAL = 'pending_group_approval'
    COMPLETED = 'completed'
    PAUSED = 'paused'
    CANCELLED = 'cancelled'
    REJECTED = 'rejected'


class EvaluationType(Enum):
    """Evaluation type enumeration"""
    NEW_PRODUCT = 'new_product'
    MASS_PRODUCTION = 'mass_production'


class Evaluation(db.Model):
    """
    Main evaluation model for product evaluations
    
    Supports two types of evaluations:
    1. New Product: DOE, PPQ, PRQ (parallel) -> Part Leader -> Group Leader approval
    2. Mass Production: Production Test -> AQL -> Pass (no approval needed)
    """
    
    __tablename__ = 'evaluations'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Evaluation identification
    evaluation_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    evaluation_type = db.Column(db.Enum('new_product', 'mass_production', name='evaluation_types'), 
                               nullable=False)
    
    # Product information
    product_name = db.Column(db.String(100), nullable=False)
    part_number = db.Column(db.String(50), nullable=False)
    
    # Evaluation details
    evaluation_reason = db.Column(db.Text)
    remarks = db.Column(db.Text)
    
    # Status and workflow
    status = db.Column(db.Enum('draft', 'in_progress', 'pending_part_approval', 'pending_group_approval', 
                              'completed', 'paused', 'cancelled', 'rejected', name='evaluation_status'), 
                      nullable=False, default='draft')
    
    # Dates
    start_date = db.Column(db.Date, nullable=False)
    completion_date = db.Column(db.Date)
    
    # User relationships
    evaluator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    part_approver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group_approver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    details = db.relationship('EvaluationDetail', backref='evaluation', lazy='dynamic', cascade='all, delete-orphan')
    results = db.relationship('EvaluationResult', backref='evaluation', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, evaluation_number, evaluation_type, product_name, part_number, 
                 evaluator_id, start_date, **kwargs):
        """
        Initialize evaluation with required fields
        
        Args:
            evaluation_number (str): Unique evaluation identifier
            evaluation_type (str): Type of evaluation ('new_product' or 'mass_production')
            product_name (str): Product name
            part_number (str): Product part number
            evaluator_id (int): ID of the evaluator
            start_date (date): Evaluation start date
        """
        self.evaluation_number = evaluation_number
        self.evaluation_type = evaluation_type
        self.product_name = product_name
        self.part_number = part_number
        self.evaluator_id = evaluator_id
        self.start_date = start_date
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def can_be_approved_by(self, user):
        """
        Check if user can approve this evaluation
        
        Args:
            user (User): User object to check
            
        Returns:
            bool: True if user can approve, False otherwise
        """
        if self.evaluation_type == 'mass_production':
            return False  # Mass production evaluations don't need approval
        
        if self.status == 'pending_part_approval':
            return user.has_permission('part_leader')
        elif self.status == 'pending_group_approval':
            return user.has_permission('group_leader')
        
        return False
    
    def approve(self, approver_id, approval_level):
        """
        Approve evaluation at specified level
        
        Args:
            approver_id (int): ID of the approver
            approval_level (str): 'part' or 'group'
        """
        if approval_level == 'part':
            self.part_approver_id = approver_id
            if self.evaluation_type == 'new_product':
                self.status = 'pending_group_approval'
        elif approval_level == 'group':
            self.group_approver_id = approver_id
            self.status = 'completed'
            self.completion_date = datetime.utcnow().date()
    
    def reject(self):
        """Reject the evaluation"""
        self.status = 'rejected'
    
    def complete(self):
        """Mark evaluation as completed (for mass production)"""
        self.status = 'completed'
        self.completion_date = datetime.utcnow().date()
    
    def pause(self):
        """Pause the evaluation"""
        self.status = 'paused'
    
    def cancel(self):
        """Cancel the evaluation"""
        self.status = 'cancelled'
    
    def resume(self):
        """Resume paused evaluation"""
        if self.status == 'paused':
            self.status = 'in_progress'
    
    def get_next_approver_role(self):
        """
        Get the role of next required approver
        
        Returns:
            str: Role name or None if no approval needed
        """
        if self.evaluation_type == 'mass_production':
            return None
        
        if self.status == 'pending_part_approval':
            return 'part_leader'
        elif self.status == 'pending_group_approval':
            return 'group_leader'
        
        return None
    
    def to_dict(self, include_details=False):
        """
        Convert evaluation to dictionary
        
        Args:
            include_details (bool): Whether to include related details and results
            
        Returns:
            dict: Evaluation data dictionary
        """
        data = {
            'id': self.id,
            'evaluation_number': self.evaluation_number,
            'evaluation_type': self.evaluation_type,
            'product_name': self.product_name,
            'part_number': self.part_number,
            'evaluation_reason': self.evaluation_reason,
            'remarks': self.remarks,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'evaluator_id': self.evaluator_id,
            'part_approver_id': self.part_approver_id,
            'group_approver_id': self.group_approver_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_details:
            data['details'] = [detail.to_dict() for detail in self.details]
            data['results'] = [result.to_dict() for result in self.results]
        
        return data
    
    def __repr__(self):
        return f'<Evaluation {self.evaluation_number}>'


class EvaluationDetail(db.Model):
    """
    Detailed information for specific evaluation types (PGM, Material, etc.)
    """
    
    __tablename__ = 'evaluation_details'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.id'), nullable=False)
    
    # Detail type and information
    detail_type = db.Column(db.Enum('pgm', 'material', 'equipment', name='detail_types'), nullable=False)
    
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
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert detail to dictionary"""
        return {
            'id': self.id,
            'evaluation_id': self.evaluation_id,
            'detail_type': self.detail_type,
            'pgm_version_before': self.pgm_version_before,
            'pgm_version_after': self.pgm_version_after,
            'material_name': self.material_name,
            'material_number': self.material_number,
            'equipment_name': self.equipment_name,
            'equipment_number': self.equipment_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<EvaluationDetail {self.detail_type} for Evaluation {self.evaluation_id}>'


class EvaluationResult(db.Model):
    """
    Test results for evaluations (DOE, PPQ, PRQ, Production Test, AQL)
    """
    
    __tablename__ = 'evaluation_results'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.id'), nullable=False)
    
    # Result type and data
    result_type = db.Column(db.Enum('doe', 'ppq', 'prq', 'production_test', 'aql', name='result_types'), 
                           nullable=False)
    result_status = db.Column(db.Enum('pass', 'fail', 'pending', name='result_status'), 
                             nullable=False, default='pending')
    result_data = db.Column(db.JSON)  # Store detailed test results as JSON
    test_date = db.Column(db.Date)
    
    # Comments and notes
    comments = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert result to dictionary"""
        return {
            'id': self.id,
            'evaluation_id': self.evaluation_id,
            'result_type': self.result_type,
            'result_status': self.result_status,
            'result_data': self.result_data,
            'test_date': self.test_date.isoformat() if self.test_date else None,
            'comments': self.comments,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<EvaluationResult {self.result_type} for Evaluation {self.evaluation_id}>' 
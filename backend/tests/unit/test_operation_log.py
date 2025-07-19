"""
Unit tests for the OperationLog model and functionality.
"""
import json
from datetime import datetime
from app.models.operation_log import OperationLog, OperationType
from app.models.evaluation import Evaluation
from tests.helpers import create_test_evaluation


def test_operation_log_creation(session, admin_user):
    """Test creating a new operation log."""
    log = OperationLog(
        user_id=admin_user.id,
        operation_type=OperationType.CREATE.value,
        target_type='evaluation',
        target_id=1,
        target_description='Created evaluation EV-20250101-001',
        operation_description='Created a new evaluation',
        ip_address='127.0.0.1',
        user_agent='Test Agent',
        success=True
    )
    session.add(log)
    session.commit()
    
    # Retrieve the log from the database
    retrieved_log = session.query(OperationLog).filter_by(user_id=admin_user.id).first()
    
    assert retrieved_log is not None
    assert retrieved_log.operation_type == OperationType.CREATE.value
    assert retrieved_log.target_type == 'evaluation'
    assert retrieved_log.target_id == 1
    assert retrieved_log.target_description == 'Created evaluation EV-20250101-001'
    assert retrieved_log.operation_description == 'Created a new evaluation'
    assert retrieved_log.ip_address == '127.0.0.1'
    assert retrieved_log.user_agent == 'Test Agent'
    assert retrieved_log.success is True


def test_operation_log_with_data(session, admin_user):
    """Test operation log with old and new data."""
    old_data = {'status': 'draft', 'product_name': 'Old Product'}
    new_data = {'status': 'in_progress', 'product_name': 'New Product'}
    
    log = OperationLog(
        user_id=admin_user.id,
        operation_type=OperationType.UPDATE.value,
        target_type='evaluation',
        target_id=1,
        target_description='Updated evaluation EV-20250101-001',
        operation_description='Updated evaluation status',
        old_data=json.dumps(old_data),
        new_data=json.dumps(new_data),
        ip_address='127.0.0.1',
        user_agent='Test Agent',
        success=True
    )
    session.add(log)
    session.commit()
    
    # Retrieve the log from the database
    retrieved_log = session.query(OperationLog).filter_by(operation_type=OperationType.UPDATE.value).first()
    
    assert retrieved_log is not None
    assert json.loads(retrieved_log.old_data) == old_data
    assert json.loads(retrieved_log.new_data) == new_data


def test_operation_log_relationship_with_evaluation(session, admin_user, regular_user):
    """Test the relationship between OperationLog and Evaluation."""
    # Create an evaluation
    evaluation = create_test_evaluation(session, regular_user.id)
    
    # Create an operation log for the evaluation
    log = OperationLog(
        user_id=admin_user.id,
        operation_type=OperationType.VIEW.value,
        target_type='evaluation',
        target_id=evaluation.id,
        target_description=f'Viewed evaluation {evaluation.evaluation_number}',
        operation_description='Viewed evaluation details',
        ip_address='127.0.0.1',
        user_agent='Test Agent',
        success=True
    )
    session.add(log)
    session.commit()
    
    # Retrieve the evaluation with its logs
    retrieved_evaluation = session.query(Evaluation).filter_by(id=evaluation.id).first()
    
    assert retrieved_evaluation is not None
    assert retrieved_evaluation.operation_logs.count() == 1
    
    log_entry = retrieved_evaluation.operation_logs.first()
    assert log_entry.operation_type == OperationType.VIEW.value
    assert log_entry.user_id == admin_user.id


def test_operation_log_to_dict(session, admin_user):
    """Test the to_dict method of the OperationLog model."""
    log = OperationLog(
        user_id=admin_user.id,
        operation_type=OperationType.DELETE.value,
        target_type='evaluation',
        target_id=1,
        target_description='Deleted evaluation EV-20250101-001',
        operation_description='Deleted an evaluation',
        ip_address='127.0.0.1',
        user_agent='Test Agent',
        success=True
    )
    session.add(log)
    session.commit()
    
    log_dict = log.to_dict()
    
    assert log_dict['user_id'] == admin_user.id
    assert log_dict['operation_type'] == OperationType.DELETE.value
    assert log_dict['target_type'] == 'evaluation'
    assert log_dict['target_id'] == 1
    assert log_dict['target_description'] == 'Deleted evaluation EV-20250101-001'
    assert log_dict['operation_description'] == 'Deleted an evaluation'
    assert log_dict['ip_address'] == '127.0.0.1'
    assert log_dict['user_agent'] == 'Test Agent'
    assert log_dict['success'] is True
    assert 'created_at' in log_dict
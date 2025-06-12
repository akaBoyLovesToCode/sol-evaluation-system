"""
Workflow Service for Product Evaluation System

This service handles the evaluation workflow engine, approval processes,
and status management as specified in Phase 2 requirements.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from flask import current_app
from app import db
from app.models.evaluation import Evaluation, EvaluationStatus, EvaluationType
from app.models.user import User, UserRole
from app.models.operation_log import OperationLog, OperationType
from app.models.message import Message, MessageType, MessageStatus


class WorkflowService:
    """
    Service class for managing evaluation workflows and approval processes
    
    Handles:
    - Evaluation status transitions
    - Approval workflow (Part Leader → Group Leader)
    - Automatic notifications
    - Workflow validation
    """
    
    # Define valid status transitions for workflow
    VALID_TRANSITIONS = {
        EvaluationStatus.IN_PROGRESS: [EvaluationStatus.PENDING_PART_APPROVAL, EvaluationStatus.COMPLETED, EvaluationStatus.PAUSED, EvaluationStatus.CANCELLED],
        EvaluationStatus.PENDING_PART_APPROVAL: [EvaluationStatus.PENDING_GROUP_APPROVAL, EvaluationStatus.REJECTED, EvaluationStatus.IN_PROGRESS],
        EvaluationStatus.PENDING_GROUP_APPROVAL: [EvaluationStatus.COMPLETED, EvaluationStatus.REJECTED, EvaluationStatus.PENDING_PART_APPROVAL],
        EvaluationStatus.PAUSED: [EvaluationStatus.IN_PROGRESS, EvaluationStatus.CANCELLED],
        EvaluationStatus.REJECTED: [EvaluationStatus.IN_PROGRESS],
        EvaluationStatus.COMPLETED: [],  # Final state
        EvaluationStatus.CANCELLED: []   # Final state
    }
    
    # Define required approvers for each transition
    APPROVAL_REQUIREMENTS = {
        (EvaluationStatus.IN_PROGRESS, EvaluationStatus.PENDING_PART_APPROVAL): [UserRole.USER, UserRole.PART_LEADER, UserRole.GROUP_LEADER, UserRole.ADMIN],
        (EvaluationStatus.PENDING_PART_APPROVAL, EvaluationStatus.PENDING_GROUP_APPROVAL): [UserRole.PART_LEADER, UserRole.GROUP_LEADER, UserRole.ADMIN],
        (EvaluationStatus.PENDING_GROUP_APPROVAL, EvaluationStatus.COMPLETED): [UserRole.GROUP_LEADER, UserRole.ADMIN],
        (EvaluationStatus.IN_PROGRESS, EvaluationStatus.COMPLETED): [UserRole.GROUP_LEADER, UserRole.ADMIN],  # For mass production
        (EvaluationStatus.PENDING_PART_APPROVAL, EvaluationStatus.REJECTED): [UserRole.PART_LEADER, UserRole.GROUP_LEADER, UserRole.ADMIN],
        (EvaluationStatus.PENDING_GROUP_APPROVAL, EvaluationStatus.REJECTED): [UserRole.GROUP_LEADER, UserRole.ADMIN],
        (EvaluationStatus.IN_PROGRESS, EvaluationStatus.PAUSED): [UserRole.USER, UserRole.PART_LEADER, UserRole.GROUP_LEADER, UserRole.ADMIN],
        (EvaluationStatus.IN_PROGRESS, EvaluationStatus.CANCELLED): [UserRole.PART_LEADER, UserRole.GROUP_LEADER, UserRole.ADMIN],
        (EvaluationStatus.PAUSED, EvaluationStatus.IN_PROGRESS): [UserRole.USER, UserRole.PART_LEADER, UserRole.GROUP_LEADER, UserRole.ADMIN],
        (EvaluationStatus.REJECTED, EvaluationStatus.IN_PROGRESS): [UserRole.USER, UserRole.PART_LEADER, UserRole.GROUP_LEADER, UserRole.ADMIN]
    }
    
    @staticmethod
    def can_transition(evaluation: Evaluation, new_status: EvaluationStatus, user: User) -> Tuple[bool, str]:
        """
        Check if an evaluation can transition to a new status
        
        Args:
            evaluation: The evaluation to check
            new_status: The target status
            user: The user requesting the transition
            
        Returns:
            Tuple of (can_transition: bool, reason: str)
        """
        # Convert string status to enum for comparison
        try:
            current_status = EvaluationStatus(evaluation.status)
        except ValueError:
            return False, f"Invalid current status: {evaluation.status}"
        
        # Check if transition is valid
        if new_status not in WorkflowService.VALID_TRANSITIONS.get(current_status, []):
            return False, f"Invalid transition from {current_status.value} to {new_status.value}"
        
        # Check user permissions for this transition
        transition_key = (current_status, new_status)
        required_roles = WorkflowService.APPROVAL_REQUIREMENTS.get(transition_key, [])
        
        # Convert user role string to enum for comparison
        try:
            user_role = UserRole(user.role)
        except ValueError:
            return False, f"Invalid user role: {user.role}"
        
        if required_roles and user_role not in required_roles:
            return False, f"User role {user_role.value} not authorized for this transition"
        
        # Additional business logic checks can be added here if needed
        # For now, we'll allow transitions based on role permissions only
        
        return True, "Transition allowed"
    
    @staticmethod
    def transition_status(evaluation_id: int, new_status: EvaluationStatus, 
                         user_id: int, comment: Optional[str] = None) -> Tuple[bool, str]:
        """
        Transition an evaluation to a new status
        
        Args:
            evaluation_id: ID of the evaluation
            new_status: Target status
            user_id: ID of the user making the transition
            comment: Optional comment for the transition
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            evaluation = Evaluation.query.get(evaluation_id)
            if not evaluation:
                return False, "Evaluation not found"
            
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"
            
            # Check if transition is allowed
            can_transition, reason = WorkflowService.can_transition(evaluation, new_status, user)
            if not can_transition:
                return False, reason
            
            old_status = evaluation.status
            evaluation.status = new_status.value  # Store as string in database
            evaluation.updated_at = datetime.utcnow()
            
            # Set completion time if completed
            if new_status == EvaluationStatus.COMPLETED:
                evaluation.completion_date = datetime.utcnow().date()
            
            # Log the operation
            log_entry = OperationLog(
                user_id=user_id,
                operation_type=OperationType.UPDATE.value,
                target_type='evaluation',
                target_id=evaluation_id,
                operation_description=f"Status changed from {old_status} to {new_status.value}",
                old_data={'status': old_status},
                new_data={'status': new_status.value}
            )
            
            db.session.add(log_entry)
            db.session.commit()
            
            # Send notifications for status changes
            WorkflowService._send_status_change_notifications(evaluation, old_status, new_status.value, user)
            
            return True, f"Status successfully changed to {new_status.value}"
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error transitioning evaluation status: {str(e)}")
            return False, f"Error updating status: {str(e)}"
    
    @staticmethod
    def _send_status_change_notifications(evaluation: Evaluation, old_status: str, 
                                        new_status: str, actor: User):
        """
        Send notifications for status changes
        
        Args:
            evaluation: The evaluation that changed
            old_status: Previous status
            new_status: New status
            actor: User who made the change
        """
        try:
            # Determine who should be notified
            recipients = []
            
            # Always notify the evaluator if different from actor
            if evaluation.evaluator_id != actor.id:
                recipients.append(evaluation.evaluator_id)
            
            # Status-specific notifications
            if new_status == 'pending_part_approval':
                # Notify part leader for approval
                if evaluation.part_approver_id and evaluation.part_approver_id != actor.id:
                    recipients.append(evaluation.part_approver_id)
            
            elif new_status == 'pending_group_approval':
                # Notify group leader for approval
                if evaluation.group_approver_id and evaluation.group_approver_id != actor.id:
                    recipients.append(evaluation.group_approver_id)
            
            elif new_status == 'completed':
                # Notify all stakeholders of completion
                stakeholders = [evaluation.evaluator_id, evaluation.part_approver_id, evaluation.group_approver_id]
                for stakeholder in stakeholders:
                    if stakeholder and stakeholder != actor.id:
                        recipients.append(stakeholder)
            
            elif new_status == 'rejected':
                # Notify evaluator of rejection
                if evaluation.evaluator_id != actor.id:
                    recipients.append(evaluation.evaluator_id)
            
            # Remove duplicates
            recipients = list(set(recipients))
            
            # Create notification messages
            for recipient_id in recipients:
                message = Message(
                    title=f"Evaluation Status Changed: {evaluation.evaluation_number}",
                    content=f"Evaluation '{evaluation.evaluation_number}' status changed from {old_status} to {new_status}",
                    message_type=MessageType.SYSTEM.value,
                    recipient_id=recipient_id,
                    sender_id=actor.id,
                    evaluation_id=evaluation.id
                )
                db.session.add(message)
            
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"Error sending status change notifications: {str(e)}")
    
    @staticmethod
    def get_pending_approvals(user_id: int) -> List[Dict]:
        """
        Get evaluations pending approval for a specific user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of evaluations pending approval
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return []
            
            query = db.session.query(Evaluation)
            
            # Filter based on user role and evaluation status
            if user.role == 'part_leader':
                # Part leaders see evaluations pending part approval
                query = query.filter(
                    Evaluation.status == 'pending_part_approval'
                )
            elif user.role == 'group_leader':
                # Group leaders see evaluations pending group approval
                query = query.filter(
                    Evaluation.status == 'pending_group_approval'
                )
            else:
                # Regular users don't have approval permissions
                return []
            
            evaluations = query.order_by(Evaluation.created_at.desc()).all()
            
            result = []
            for eval in evaluations:
                result.append({
                    'id': eval.id,
                    'evaluation_number': eval.evaluation_number,
                    'product_name': eval.product_name,
                    'part_number': eval.part_number,
                    'evaluation_type': eval.evaluation_type,
                    'status': eval.status,
                    'created_at': eval.created_at.isoformat(),
                    'start_date': eval.start_date.isoformat() if eval.start_date else None,
                    'evaluator': eval.evaluator.full_name if eval.evaluator else None,
                    'days_pending': (datetime.utcnow() - eval.created_at).days
                })
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error getting pending approvals: {str(e)}")
            return []
    
    @staticmethod
    def get_workflow_statistics() -> Dict:
        """
        Get workflow statistics for dashboard
        
        Returns:
            Dictionary with workflow statistics
        """
        try:
            stats = {}
            
            # Count evaluations by status
            for status in EvaluationStatus:
                count = Evaluation.query.filter_by(status=status.value).count()
                stats[f"{status.value.lower()}_count"] = count
            
            # Average processing time for completed evaluations
            completed_evals = Evaluation.query.filter(
                and_(
                    Evaluation.status == 'completed',
                    Evaluation.completion_date.isnot(None)
                )
            ).all()
            
            if completed_evals:
                total_days = sum([
                    (eval.completion_date - eval.start_date).days 
                    for eval in completed_evals
                    if eval.completion_date and eval.start_date
                ])
                stats['average_completion_days'] = round(total_days / len(completed_evals), 1) if total_days > 0 else 0
            else:
                stats['average_completion_days'] = 0
            
            # Evaluations by type
            for eval_type in EvaluationType:
                count = Evaluation.query.filter_by(evaluation_type=eval_type.value).count()
                stats[f"{eval_type.value.lower().replace(' ', '_')}_count"] = count
            
            return stats
            
        except Exception as e:
            current_app.logger.error(f"Error getting workflow statistics: {str(e)}")
            return {}
    
    @staticmethod
    def auto_assign_evaluations():
        """
        Automatically assign evaluations based on workload and availability
        This method can be called by a scheduled task
        """
        try:
            # Get evaluations that need assignment (in progress but no evaluator assigned)
            unassigned = Evaluation.query.filter(
                and_(
                    Evaluation.evaluator_id.is_(None),
                    Evaluation.status == 'in_progress'
                )
            ).all()
            
            if not unassigned:
                return
            
            # Get available users (not admins)
            available_users = User.query.filter(
                and_(
                    User.is_active == True,
                    User.role.in_(['user', 'part_leader'])
                )
            ).all()
            
            if not available_users:
                return
            
            # Simple round-robin assignment based on current workload
            user_workloads = {}
            for user in available_users:
                workload = Evaluation.query.filter(
                    and_(
                        Evaluation.evaluator_id == user.id,
                        Evaluation.status.in_(['in_progress', 'pending_part_approval', 'pending_group_approval'])
                    )
                ).count()
                user_workloads[user.id] = workload
            
            # Sort users by workload (ascending)
            sorted_users = sorted(user_workloads.items(), key=lambda x: x[1])
            
            # Assign evaluations to users with lowest workload
            for i, evaluation in enumerate(unassigned):
                user_id = sorted_users[i % len(sorted_users)][0]
                evaluation.evaluator_id = user_id
                
                # Log the auto-assignment
                log_entry = OperationLog(
                    user_id=1,  # System user
                    operation_type=OperationType.UPDATE.value,
                    target_type='evaluation',
                    target_id=evaluation.id,
                    operation_description="Auto-assigned evaluation based on workload balancing",
                    old_data={'evaluator_id': None},
                    new_data={'evaluator_id': user_id}
                )
                db.session.add(log_entry)
            
            db.session.commit()
            current_app.logger.info(f"Auto-assigned {len(unassigned)} evaluations")
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error in auto-assignment: {str(e)}") 
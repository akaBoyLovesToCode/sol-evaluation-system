"""Workflow API endpoints for Product Evaluation System

This module handles workflow-related API endpoints including status transitions,
approvals, and workflow statistics.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.models.user import User
from app.models.evaluation import Evaluation, EvaluationStatus
from app.services.workflow_service import WorkflowService
from app.utils.decorators import role_required, validate_json
from app.utils.helpers import get_current_user_id

# Create blueprint
workflow_bp = Blueprint("workflow", __name__)


@workflow_bp.route("/transition", methods=["POST"])
@jwt_required()
@validate_json(["evaluation_id", "new_status"])
def transition_evaluation_status():
    """Transition an evaluation to a new status

    Required JSON fields:
    - evaluation_id: int
    - new_status: str
    - comment: str (optional)
    """
    try:
        data = request.get_json()
        current_user_id = get_current_user_id()

        evaluation_id = data["evaluation_id"]
        new_status_str = data["new_status"]
        comment = data.get("comment")

        # Validate status
        try:
            new_status = EvaluationStatus(new_status_str)
        except ValueError:
            return jsonify(
                {
                    "error": f"Invalid status: {new_status_str}",
                    "valid_statuses": [status.value for status in EvaluationStatus],
                }
            ), 400

        # Perform status transition
        success, message = WorkflowService.transition_status(
            evaluation_id=evaluation_id,
            new_status=new_status,
            user_id=current_user_id,
            comment=comment,
        )

        if success:
            return jsonify(
                {
                    "message": message,
                    "evaluation_id": evaluation_id,
                    "new_status": new_status.value,
                }
            ), 200
        else:
            return jsonify({"error": message}), 400

    except Exception as e:
        current_app.logger.error(f"Error in status transition: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@workflow_bp.route("/pending-approvals", methods=["GET"])
@jwt_required()
def get_pending_approvals():
    """Get evaluations pending approval for the current user
    """
    try:
        current_user_id = get_current_user_id()

        # Get pending approvals for the user
        pending_approvals = WorkflowService.get_pending_approvals(current_user_id)

        return jsonify(
            {"pending_approvals": pending_approvals, "count": len(pending_approvals)}
        ), 200

    except Exception as e:
        current_app.logger.error(f"Error getting pending approvals: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@workflow_bp.route("/statistics", methods=["GET"])
@jwt_required()
@role_required(["Admin", "Group Leader", "Part Leader"])
def get_workflow_statistics():
    """Get workflow statistics (for leaders and admins)
    """
    try:
        # Get workflow statistics
        stats = WorkflowService.get_workflow_statistics()

        return jsonify({"statistics": stats}), 200

    except Exception as e:
        current_app.logger.error(f"Error getting workflow statistics: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@workflow_bp.route("/can-transition", methods=["POST"])
@jwt_required()
@validate_json(["evaluation_id", "new_status"])
def check_transition_permission():
    """Check if current user can transition an evaluation to a new status

    Required JSON fields:
    - evaluation_id: int
    - new_status: str
    """
    try:
        data = request.get_json()
        current_user_id = get_current_user_id()

        evaluation_id = data["evaluation_id"]
        new_status_str = data["new_status"]

        # Get evaluation and user
        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return jsonify({"error": "Evaluation not found"}), 404

        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Validate status
        try:
            new_status = EvaluationStatus(new_status_str)
        except ValueError:
            return jsonify(
                {
                    "error": f"Invalid status: {new_status_str}",
                    "valid_statuses": [status.value for status in EvaluationStatus],
                }
            ), 400

        # Check if transition is allowed
        can_transition, reason = WorkflowService.can_transition(
            evaluation, new_status, user
        )

        return jsonify(
            {
                "can_transition": can_transition,
                "reason": reason,
                "current_status": evaluation.status.value,
                "target_status": new_status.value,
            }
        ), 200

    except Exception as e:
        current_app.logger.error(f"Error checking transition permission: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@workflow_bp.route("/auto-assign", methods=["POST"])
@jwt_required()
@role_required(["Admin", "Group Leader"])
def trigger_auto_assignment():
    """Trigger automatic assignment of unassigned evaluations
    (Admin and Group Leader only)
    """
    try:
        # Trigger auto-assignment
        WorkflowService.auto_assign_evaluations()

        return jsonify({"message": "Auto-assignment completed successfully"}), 200

    except Exception as e:
        current_app.logger.error(f"Error in auto-assignment: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@workflow_bp.route("/bulk-transition", methods=["POST"])
@jwt_required()
@role_required(["Admin", "Group Leader", "Part Leader"])
@validate_json(["evaluation_ids", "new_status"])
def bulk_transition_status():
    """Transition multiple evaluations to a new status
    (Leaders and Admin only)

    Required JSON fields:
    - evaluation_ids: List[int]
    - new_status: str
    - comment: str (optional)
    """
    try:
        data = request.get_json()
        current_user_id = get_current_user_id()

        evaluation_ids = data["evaluation_ids"]
        new_status_str = data["new_status"]
        comment = data.get("comment")

        # Validate inputs
        if not isinstance(evaluation_ids, list) or not evaluation_ids:
            return jsonify({"error": "evaluation_ids must be a non-empty list"}), 400

        try:
            new_status = EvaluationStatus(new_status_str)
        except ValueError:
            return jsonify(
                {
                    "error": f"Invalid status: {new_status_str}",
                    "valid_statuses": [status.value for status in EvaluationStatus],
                }
            ), 400

        # Process each evaluation
        results = []
        success_count = 0

        for eval_id in evaluation_ids:
            success, message = WorkflowService.transition_status(
                evaluation_id=eval_id,
                new_status=new_status,
                user_id=current_user_id,
                comment=comment,
            )

            results.append(
                {"evaluation_id": eval_id, "success": success, "message": message}
            )

            if success:
                success_count += 1

        return jsonify(
            {
                "message": f"Bulk transition completed: {success_count}/{len(evaluation_ids)} successful",
                "results": results,
                "success_count": success_count,
                "total_count": len(evaluation_ids),
            }
        ), 200

    except Exception as e:
        current_app.logger.error(f"Error in bulk transition: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@workflow_bp.route("/history/<int:evaluation_id>", methods=["GET"])
@jwt_required()
def get_workflow_history(evaluation_id):
    """Get workflow history for a specific evaluation
    """
    try:
        # Check if evaluation exists
        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return jsonify({"error": "Evaluation not found"}), 404

        # Get operation logs for this evaluation
        from app.models.operation_log import OperationLog

        logs = (
            OperationLog.query.filter_by(
                table_name="evaluations", record_id=evaluation_id
            )
            .order_by(OperationLog.created_at.desc())
            .all()
        )

        history = []
        for log in logs:
            history.append(
                {
                    "id": log.id,
                    "operation_type": log.operation_type.value,
                    "description": log.description,
                    "old_values": log.old_values,
                    "new_values": log.new_values,
                    "comment": log.comment,
                    "created_at": log.created_at.isoformat(),
                    "user": log.user.username if log.user else "System",
                }
            )

        return jsonify(
            {
                "evaluation_id": evaluation_id,
                "evaluation_title": evaluation.title,
                "current_status": evaluation.status.value,
                "history": history,
            }
        ), 200

    except Exception as e:
        current_app.logger.error(f"Error getting workflow history: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from app import db
from app.models import OperationLog, Evaluation, User
from app.utils.decorators import require_role, validate_json, handle_exceptions
from app.utils.helpers import (
    calculate_pagination,
    create_response,
    get_current_user_id,
)

# Create operation log blueprint
operation_log_bp = Blueprint("operation_log", __name__)


@operation_log_bp.route("/evaluations/<int:evaluation_id>/logs", methods=["GET"])
@jwt_required()
@handle_exceptions
def get_evaluation_logs(evaluation_id):
    """Get operation logs for a specific evaluation

    Query parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    - operation_type: Filter by operation type
    - user_id: Filter by user ID
    - sort_order: Sort order (asc, desc) default: desc
    """
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)

        # Check if evaluation exists
        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return create_response(message="Evaluation not found", status_code=404)

        # Check permissions
        if (
            not current_user.has_permission("part_leader")
            and evaluation.evaluator_id != current_user_id
        ):
            return create_response(message="Permission denied", status_code=403)

        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        operation_type = request.args.get("operation_type")
        user_id = request.args.get("user_id", type=int)
        sort_order = request.args.get("sort_order", "desc")

        # Build query
        query = OperationLog.query.filter(
            OperationLog.target_type == "evaluation",
            OperationLog.target_id == evaluation_id,
        )

        # Apply filters
        if operation_type:
            query = query.filter(OperationLog.operation_type == operation_type)

        if user_id:
            query = query.filter(OperationLog.user_id == user_id)

        # Apply sorting
        if sort_order.lower() == "asc":
            query = query.order_by(OperationLog.created_at.asc())
        else:
            query = query.order_by(OperationLog.created_at.desc())

        # Get total count for pagination
        total_count = query.count()

        # Apply pagination
        pagination_info = calculate_pagination(page, per_page, total_count)
        logs = query.offset(pagination_info["offset"]).limit(per_page).all()

        # Convert to dictionaries
        log_list = [log.to_dict() for log in logs]

        return create_response(
            data={"logs": log_list, "pagination": pagination_info},
            message="Operation logs retrieved successfully",
        )

    except Exception as e:
        current_app.logger.error(f"Get operation logs error: {str(e)}")
        return create_response(
            message="Failed to retrieve operation logs", status_code=500
        )


@operation_log_bp.route(
    "/evaluations/<int:evaluation_id>/logs/<int:log_id>", methods=["PUT"]
)
@jwt_required()
@require_role("admin")
@validate_json(required_fields=["operation_description"])
@handle_exceptions
def update_evaluation_log(evaluation_id, log_id):
    """Update operation log (admin only)

    Request body:
    - operation_description: Updated description
    """
    try:
        current_user_id = get_current_user_id()

        # Check if evaluation exists
        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return create_response(message="Evaluation not found", status_code=404)

        # Check if log exists and belongs to the evaluation
        log = OperationLog.query.filter(
            OperationLog.id == log_id,
            OperationLog.target_type == "evaluation",
            OperationLog.target_id == evaluation_id,
        ).first()

        if not log:
            return create_response(message="Operation log not found", status_code=404)

        # Get request data
        data = request.get_json()
        operation_description = data.get("operation_description")

        # Update log
        log.operation_description = operation_description

        # Log this update operation
        ip_address = request.remote_addr
        user_agent = request.headers.get("User-Agent")
        OperationLog.log_system_operation(
            user_id=current_user_id,
            operation_description=f"Updated operation log {log_id} for evaluation {evaluation_id}",
            operation_data={"log_id": log_id, "evaluation_id": evaluation_id},
            ip_address=ip_address,
        )

        db.session.commit()

        return create_response(
            data={"log": log.to_dict()},
            message="Operation log updated successfully",
        )

    except Exception as e:
        current_app.logger.error(f"Update operation log error: {str(e)}")
        db.session.rollback()
        return create_response(
            message="Failed to update operation log", status_code=500
        )


@operation_log_bp.route("/logs", methods=["GET"])
@jwt_required()
@require_role("admin")
@handle_exceptions
def get_all_logs():
    """Get all operation logs (admin only)

    Query parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    - operation_type: Filter by operation type
    - target_type: Filter by target type
    - user_id: Filter by user ID
    - sort_order: Sort order (asc, desc) default: desc
    """
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        operation_type = request.args.get("operation_type")
        target_type = request.args.get("target_type")
        user_id = request.args.get("user_id", type=int)
        sort_order = request.args.get("sort_order", "desc")

        # Build query
        query = OperationLog.query

        # Apply filters
        if operation_type:
            query = query.filter(OperationLog.operation_type == operation_type)

        if target_type:
            query = query.filter(OperationLog.target_type == target_type)

        if user_id:
            query = query.filter(OperationLog.user_id == user_id)

        # Apply sorting
        if sort_order.lower() == "asc":
            query = query.order_by(OperationLog.created_at.asc())
        else:
            query = query.order_by(OperationLog.created_at.desc())

        # Get total count for pagination
        total_count = query.count()

        # Apply pagination
        pagination_info = calculate_pagination(page, per_page, total_count)
        logs = query.offset(pagination_info["offset"]).limit(per_page).all()

        # Convert to dictionaries
        log_list = [log.to_dict() for log in logs]

        return create_response(
            data={"logs": log_list, "pagination": pagination_info},
            message="Operation logs retrieved successfully",
        )

    except Exception as e:
        current_app.logger.error(f"Get all operation logs error: {str(e)}")
        return create_response(
            message="Failed to retrieve operation logs", status_code=500
        )

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime
from app import db
from app.models import Evaluation, EvaluationDetail, EvaluationResult, User, Message
from app.utils.decorators import require_role, validate_json, handle_exceptions
from app.utils.validators import validate_evaluation_data, validate_evaluation_detail
from app.utils.helpers import (
    generate_evaluation_number,
    parse_date_string,
    calculate_pagination,
    build_query_filters,
    create_response,
    get_current_user_id,
)

# Create evaluation blueprint
evaluation_bp = Blueprint("evaluation", __name__)


@evaluation_bp.route("", methods=["GET"])
@jwt_required()
@handle_exceptions
def get_evaluations():
    """
    Get list of evaluations with filtering and pagination

    Query parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    - status: Filter by status
    - evaluation_type: Filter by type
    - evaluator_id: Filter by evaluator
    - product: Filter by product name
    - ssd_product: Filter by product name (deprecated, use 'product' instead)
    - start_date_from: Filter by start date (from)
    - start_date_to: Filter by start date (to)
    """
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)

        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        # Build base query
        query = Evaluation.query

        # Apply role-based filtering
        if not current_user.has_permission("part_leader"):
            # Regular users can only see their own evaluations
            query = query.filter(Evaluation.evaluator_id == current_user_id)

        # Apply filters
        filters = {}

        if request.args.get("status"):
            filters["status"] = request.args.get("status")

        if request.args.get("evaluation_type"):
            filters["evaluation_type"] = request.args.get("evaluation_type")

        if request.args.get("evaluator_id"):
            filters["evaluator_id"] = request.args.get("evaluator_id", type=int)

        # Support both new product field and deprecated ssd_product field
        if request.args.get("product"):
            filters["product_name"] = {"like": request.args.get("product")}
        elif request.args.get("ssd_product"):
            filters["product_name"] = {"like": request.args.get("ssd_product")}

        # Date range filters
        start_date_from = request.args.get("start_date_from")
        start_date_to = request.args.get("start_date_to")

        if start_date_from:
            date_from = parse_date_string(start_date_from)
            if date_from:
                filters["start_date"] = filters.get("start_date", {})
                filters["start_date"]["gte"] = date_from

        if start_date_to:
            date_to = parse_date_string(start_date_to)
            if date_to:
                filters["start_date"] = filters.get("start_date", {})
                filters["start_date"]["lte"] = date_to

        # Apply filters to query
        filter_conditions = build_query_filters(Evaluation, filters)
        for condition in filter_conditions:
            query = query.filter(condition)

        # Order by creation date (newest first)
        query = query.order_by(Evaluation.created_at.desc())

        # Get total count for pagination
        total_count = query.count()

        # Apply pagination
        pagination_info = calculate_pagination(page, per_page, total_count)
        evaluations = query.offset(pagination_info["offset"]).limit(per_page).all()

        # Convert to dictionaries
        evaluation_list = []
        for evaluation in evaluations:
            eval_dict = evaluation.to_dict()
            # Add evaluator name
            eval_dict["evaluator_name"] = evaluation.evaluator.full_name
            evaluation_list.append(eval_dict)

        return create_response(
            data={"evaluations": evaluation_list, "pagination": pagination_info},
            message="Evaluations retrieved successfully",
        )

    except Exception as e:
        current_app.logger.error(f"Get evaluations error: {str(e)}")
        return create_response(
            message="Failed to retrieve evaluations", status_code=500
        )


@evaluation_bp.route("/<int:evaluation_id>", methods=["GET"])
@jwt_required()
@handle_exceptions
def get_evaluation(evaluation_id):
    """Get single evaluation by ID with details"""
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)

        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return create_response(message="Evaluation not found", status_code=404)

        # Check permissions
        if (
            not current_user.has_permission("part_leader")
            and evaluation.evaluator_id != current_user_id
        ):
            return create_response(message="Permission denied", status_code=403)

        # Get evaluation with details
        eval_dict = evaluation.to_dict(include_details=True)
        eval_dict["evaluator_name"] = evaluation.evaluator.full_name

        # Add approver names if available
        if evaluation.part_approver_id:
            part_approver = User.query.get(evaluation.part_approver_id)
            eval_dict["part_approver_name"] = (
                part_approver.full_name if part_approver else None
            )

        if evaluation.group_approver_id:
            group_approver = User.query.get(evaluation.group_approver_id)
            eval_dict["group_approver_name"] = (
                group_approver.full_name if group_approver else None
            )

        return create_response(
            data={"evaluation": eval_dict}, message="Evaluation retrieved successfully"
        )

    except Exception as e:
        current_app.logger.error(f"Get evaluation error: {str(e)}")
        return create_response(message="Failed to retrieve evaluation", status_code=500)


@evaluation_bp.route("", methods=["POST"])
@jwt_required()
@validate_json(
    required_fields=["evaluation_type", "product_name", "part_number", "start_date"]
)
@handle_exceptions
def create_evaluation():
    """Create new evaluation"""
    try:
        current_user_id = get_current_user_id()
        data = request.get_json()

        # Validate evaluation data
        validation_result = validate_evaluation_data(data, data["evaluation_type"])
        if not validation_result["valid"]:
            return create_response(
                message="Validation failed",
                errors=validation_result["errors"],
                status_code=400,
            )

        # Parse start date
        start_date = parse_date_string(data["start_date"])
        if not start_date:
            return create_response(
                message="Invalid start date format. Use YYYY-MM-DD", status_code=400
            )

        # Generate evaluation number
        evaluation_number = generate_evaluation_number()

        # Create evaluation
        evaluation = Evaluation(
            evaluation_number=evaluation_number,
            evaluation_type=data["evaluation_type"],
            product_name=data.get("product_name", data.get("ssd_product", "")).strip(),
            part_number=data["part_number"].strip(),
            evaluator_id=current_user_id,
            start_date=start_date,
            evaluation_reason=data.get("evaluation_reason", "").strip(),
            remarks=data.get("remarks", "").strip(),
            status=data.get("status", "draft"),
        )

        db.session.add(evaluation)
        db.session.flush()  # Get the ID

        # Add evaluation details if provided
        details_data = data.get("details", [])
        for detail_data in details_data:
            detail_type = detail_data.get("detail_type")
            if not detail_type:
                continue

            # Validate detail data
            detail_validation = validate_evaluation_detail(detail_data, detail_type)
            if not detail_validation["valid"]:
                db.session.rollback()
                return create_response(
                    message="Detail validation failed",
                    errors=detail_validation["errors"],
                    status_code=400,
                )

            # Create detail
            detail = EvaluationDetail(
                evaluation_id=evaluation.id,
                detail_type=detail_type,
                pgm_version_before=detail_data.get("pgm_version_before"),
                pgm_version_after=detail_data.get("pgm_version_after"),
                material_name=detail_data.get("material_name"),
                material_number=detail_data.get("material_number"),
                equipment_name=detail_data.get("equipment_name"),
                equipment_number=detail_data.get("equipment_number"),
            )
            db.session.add(detail)

        db.session.commit()

        return create_response(
            data={"evaluation": evaluation.to_dict(include_details=True)},
            message="Evaluation created successfully",
            status_code=201,
        )

    except Exception as e:
        current_app.logger.error(f"Create evaluation error: {str(e)}")
        db.session.rollback()
        return create_response(message="Failed to create evaluation", status_code=500)


@evaluation_bp.route("/<int:evaluation_id>", methods=["PUT"])
@jwt_required()
@validate_json()
@handle_exceptions
def update_evaluation(evaluation_id):
    """Update evaluation"""
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)
        data = request.get_json()

        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return create_response(message="Evaluation not found", status_code=404)

        # Check permissions
        can_edit = (
            evaluation.evaluator_id == current_user_id  # Owner
            or current_user.has_permission("admin")  # Admin
            or (
                current_user.has_permission("part_leader")
                and evaluation.status == "in_progress"
            )  # Leader for in-progress
        )

        if not can_edit:
            return create_response(message="Permission denied", status_code=403)

        # Cannot edit completed or cancelled evaluations
        if evaluation.status in ["completed", "cancelled"]:
            return create_response(
                message="Cannot edit completed or cancelled evaluations",
                status_code=400,
            )

        # Update fields
        updatable_fields = [
            "product_name",
            "part_number",
            "evaluation_reason",
            "remarks",
        ]

        for field in updatable_fields:
            if field in data:
                setattr(evaluation, field, data[field])

        # Update start date if provided
        if "start_date" in data:
            start_date = parse_date_string(data["start_date"])
            if start_date:
                evaluation.start_date = start_date

        db.session.commit()

        return create_response(
            data={"evaluation": evaluation.to_dict(include_details=True)},
            message="Evaluation updated successfully",
        )

    except Exception as e:
        current_app.logger.error(f"Update evaluation error: {str(e)}")
        db.session.rollback()
        return create_response(message="Failed to update evaluation", status_code=500)


@evaluation_bp.route("/<int:evaluation_id>/approve", methods=["POST"])
@jwt_required()
@require_role("part_leader")
@handle_exceptions
def approve_evaluation(evaluation_id):
    """Approve evaluation (Part Leader or Group Leader)"""
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)

        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return create_response(message="Evaluation not found", status_code=404)

        # Check if evaluation can be approved
        if not evaluation.can_be_approved_by(current_user):
            return create_response(
                message="Evaluation cannot be approved at this stage or by this user",
                status_code=400,
            )

        # Determine approval level
        if evaluation.status == "pending_part_approval" and current_user.has_permission(
            "part_leader"
        ):
            approval_level = "part"
        elif (
            evaluation.status == "pending_group_approval"
            and current_user.has_permission("group_leader")
        ):
            approval_level = "group"
        else:
            return create_response(message="Invalid approval request", status_code=400)

        # Approve evaluation
        old_status = evaluation.status
        evaluation.approve(current_user_id, approval_level)

        # Create notification for evaluator about approval
        if evaluation.status == "completed":
            message = Message.create_status_change(
                evaluation=evaluation,
                recipient_id=evaluation.evaluator_id,
                old_status=old_status,
                new_status=evaluation.status,
            )
            db.session.add(message)
        elif evaluation.status == "pending_group_approval":
            # Find group leaders to notify
            group_leaders = User.query.filter_by(
                role="group_leader", is_active=True
            ).all()
            for leader in group_leaders:
                message = Message.create_approval_request(
                    evaluation=evaluation,
                    recipient_id=leader.id,
                    approval_level="group",
                )
                db.session.add(message)

        db.session.commit()

        return create_response(
            data={"evaluation": evaluation.to_dict()},
            message=f"Evaluation approved by {approval_level} leader",
        )

    except Exception as e:
        current_app.logger.error(f"Approve evaluation error: {str(e)}")
        db.session.rollback()
        return create_response(message="Failed to approve evaluation", status_code=500)


@evaluation_bp.route("/<int:evaluation_id>/reject", methods=["POST"])
@jwt_required()
@require_role("part_leader")
@validate_json(optional_fields=["reason"])
@handle_exceptions
def reject_evaluation(evaluation_id):
    """Reject evaluation"""
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)
        data = request.get_json()

        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return create_response(message="Evaluation not found", status_code=404)

        # Check if evaluation can be rejected
        if not evaluation.can_be_approved_by(current_user):
            return create_response(
                message="Evaluation cannot be rejected by this user", status_code=400
            )

        # Reject evaluation
        old_status = evaluation.status
        evaluation.reject()

        # Add rejection reason to remarks
        rejection_reason = data.get("reason", "No reason provided")
        if evaluation.remarks:
            evaluation.remarks += (
                f"\n\nRejected by {current_user.full_name}: {rejection_reason}"
            )
        else:
            evaluation.remarks = (
                f"Rejected by {current_user.full_name}: {rejection_reason}"
            )

        # Create notification for evaluator
        message = Message.create_status_change(
            evaluation=evaluation,
            recipient_id=evaluation.evaluator_id,
            old_status=old_status,
            new_status=evaluation.status,
        )
        db.session.add(message)

        db.session.commit()

        return create_response(
            data={"evaluation": evaluation.to_dict()}, message="Evaluation rejected"
        )

    except Exception as e:
        current_app.logger.error(f"Reject evaluation error: {str(e)}")
        db.session.rollback()
        return create_response(message="Failed to reject evaluation", status_code=500)


@evaluation_bp.route("/<int:evaluation_id>/status", methods=["PUT"])
@jwt_required()
@validate_json(required_fields=["status"])
@handle_exceptions
def update_evaluation_status(evaluation_id):
    """Update evaluation status (pause, resume, cancel, complete)"""
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)
        data = request.get_json()

        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return create_response(message="Evaluation not found", status_code=404)

        new_status = data["status"]

        # Check permissions
        can_update = (
            evaluation.evaluator_id == current_user_id
            or current_user.has_permission("part_leader")
        )

        if not can_update:
            return create_response(message="Permission denied", status_code=403)

        old_status = evaluation.status

        # Update status based on action
        if new_status == "paused":
            evaluation.pause()
        elif new_status == "in_progress":
            evaluation.resume()
        elif new_status == "cancelled":
            evaluation.cancel()
        elif (
            new_status == "completed"
            and evaluation.evaluation_type == "mass_production"
        ):
            evaluation.complete()
        else:
            return create_response(message="Invalid status transition", status_code=400)

        # Create notification if status changed
        if old_status != evaluation.status:
            message = Message.create_status_change(
                evaluation=evaluation,
                recipient_id=evaluation.evaluator_id,
                old_status=old_status,
                new_status=evaluation.status,
            )
            db.session.add(message)

        db.session.commit()

        return create_response(
            data={"evaluation": evaluation.to_dict()},
            message=f"Evaluation status updated to {evaluation.status}",
        )

    except Exception as e:
        current_app.logger.error(f"Update evaluation status error: {str(e)}")
        db.session.rollback()
        return create_response(
            message="Failed to update evaluation status", status_code=500
        )

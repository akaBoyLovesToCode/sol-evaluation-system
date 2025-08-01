"""API endpoints for evaluation management.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, Tuple, Optional
import json

from flask import Blueprint, request, jsonify, current_app, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db
from app.models.evaluation import Evaluation, EvaluationStatus, EvaluationDetail
from app.models.user import User
from app.models.operation_log import OperationLog, OperationType

evaluation_bp = Blueprint("evaluation", __name__)


def generate_evaluation_number() -> str:
    """Generate a unique evaluation number in format: EVAL-YYYYMMDD-NNNN.
    
    Returns:
        str: Unique evaluation number formatted as EVAL-YYYYMMDD-NNNN.

    """
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")

    # Find the highest number for today
    today_prefix = f"EVAL-{date_str}-"
    latest_eval = (
        db.session.query(Evaluation)
        .filter(Evaluation.evaluation_number.like(f"{today_prefix}%"))
        .order_by(Evaluation.evaluation_number.desc())
        .first()
    )

    if latest_eval:
        # Extract the number part and increment
        try:
            last_number = int(latest_eval.evaluation_number.split("-")[-1])
            next_number = last_number + 1
        except (ValueError, IndexError):
            next_number = 1
    else:
        next_number = 1

    return f"EVAL-{date_str}-{next_number:04d}"


@evaluation_bp.route("", methods=["GET"])
@jwt_required()
def get_evaluations() -> Tuple[Response, int]:
    """Get a list of evaluations with optional filtering.
    
    Query Parameters:
        page (int, optional): Page number for pagination. Defaults to 1.
        per_page (int, optional): Number of items per page. Defaults to 10.
        status (str, optional): Filter by evaluation status.
        evaluation_type (str, optional): Filter by evaluation type.
        product_name (str, optional): Filter by product name (partial match).
        evaluator_id (int, optional): Filter by evaluator ID.
    
    Returns:
        Tuple[Response, int]: JSON response with evaluation list and HTTP status code.
        
    Raises:
        500: If database operation fails.
    ---
    tags:
      - Evaluations
    security:
      - bearerAuth: []
    parameters:
      - name: page
        in: query
        schema:
          type: integer
          default: 1
        description: Page number for pagination
      - name: per_page
        in: query
        schema:
          type: integer
          default: 10
        description: Number of items per page
      - name: status
        in: query
        schema:
          type: string
          enum: [draft, in_progress, pending_part_approval, pending_group_approval, completed, paused, cancelled, rejected]
        description: Filter by evaluation status
      - name: evaluation_type
        in: query
        schema:
          type: string
          enum: [new_product, mass_production]
        description: Filter by evaluation type
      - name: product_name
        in: query
        schema:
          type: string
        description: Filter by product name (partial match)
      - name: evaluator_id
        in: query
        schema:
          type: integer
        description: Filter by evaluator ID
    responses:
      200:
        description: List of evaluations
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                data:
                  type: object
                  properties:
                    evaluations:
                      type: array
                      items:
                        type: object
                        properties:
                          id:
                            type: integer
                          evaluation_number:
                            type: string
                          evaluation_type:
                            type: string
                          product_name:
                            type: string
                          part_number:
                            type: string
                          status:
                            type: string
                          start_date:
                            type: string
                            format: date
                          expected_end_date:
                            type: string
                            format: date
                          actual_end_date:
                            type: string
                            format: date
                          process_step:
                            type: string
                          evaluator_name:
                            type: string
                    total:
                      type: integer
                    page:
                      type: integer
                    per_page:
                      type: integer
                    pages:
                      type: integer
      401:
        description: Unauthorized
      500:
        description: Internal server error

    """
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        status = request.args.get("status")
        evaluation_type = request.args.get("evaluation_type")
        product_name = request.args.get("product_name")
        evaluator_id = request.args.get("evaluator_id", type=int)

        # Build query
        query = Evaluation.query

        # Apply filters
        if status:
            query = query.filter(Evaluation.status == status)
        if evaluation_type:
            query = query.filter(Evaluation.evaluation_type == evaluation_type)
        if product_name:
            query = query.filter(Evaluation.product_name.ilike(f"%{product_name}%"))
        if evaluator_id:
            query = query.filter(Evaluation.evaluator_id == evaluator_id)

        # Paginate results
        paginated_evaluations = query.order_by(Evaluation.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Format response
        evaluations = []
        for evaluation in paginated_evaluations.items:
            evaluator = User.query.get(evaluation.evaluator_id)
            evaluator_name = evaluator.full_name if evaluator else "Unknown"

            evaluation_data = evaluation.to_dict()
            evaluation_data["evaluator_name"] = evaluator_name
            evaluations.append(evaluation_data)

        # Log operation
        user_id = get_jwt_identity()
        log = OperationLog(
            user_id=user_id,
            operation_type=OperationType.VIEW.value,
            target_type="evaluation_list",
            target_id=None,
            target_description="Viewed evaluation list",
            operation_description=f"User viewed evaluation list with filters: {request.args}",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            success=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "data": {
                    "evaluations": evaluations,
                    "total": paginated_evaluations.total,
                    "page": page,
                    "per_page": per_page,
                    "pages": paginated_evaluations.pages,
                },
            }
        )
    except Exception as e:
        current_app.logger.error(f"Error getting evaluations: {str(e)}")
        return jsonify(
            {"success": False, "message": "Failed to get evaluations", "error": str(e)}
        ), 500


@evaluation_bp.route("/<int:evaluation_id>", methods=["GET"])
@jwt_required()
def get_evaluation(evaluation_id: int) -> Tuple[Response, int]:
    """Get details of a specific evaluation.
    
    Args:
        evaluation_id (int): ID of the evaluation to retrieve.
    
    Returns:
        Tuple[Response, int]: JSON response with evaluation details and HTTP status code.
        
    Raises:
        404: If evaluation not found.
        500: If database operation fails.
    ---
    tags:
      - Evaluations
    security:
      - bearerAuth: []
    parameters:
      - name: evaluation_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the evaluation to retrieve
    responses:
      200:
        description: Evaluation details
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                data:
                  type: object
                  properties:
                    evaluation:
                      type: object
                      properties:
                        id:
                          type: integer
                        evaluation_number:
                          type: string
                        evaluation_type:
                          type: string
                        product_name:
                          type: string
                        part_number:
                          type: string
                        status:
                          type: string
                        start_date:
                          type: string
                          format: date
                        expected_end_date:
                          type: string
                          format: date
                        actual_end_date:
                          type: string
                          format: date
                        process_step:
                          type: string
                        evaluator_name:
                          type: string
                        logs:
                          type: array
                          items:
                            type: object
      404:
        description: Evaluation not found
      401:
        description: Unauthorized
      500:
        description: Internal server error

    """
    try:
        evaluation = Evaluation.query.get(evaluation_id)

        if not evaluation:
            return jsonify({"success": False, "message": "Evaluation not found"}), 404

        # Get evaluator name
        evaluator = User.query.get(evaluation.evaluator_id)
        evaluator_name = evaluator.full_name if evaluator else "Unknown"

        # Get evaluation data
        evaluation_data = evaluation.to_dict()
        evaluation_data["evaluator_name"] = evaluator_name

        # Get operation logs
        logs = []
        for log in evaluation.operation_logs:
            user = User.query.get(log.user_id)
            log_data = log.to_dict()
            log_data["user_name"] = user.full_name if user else "Unknown"
            logs.append(log_data)

        evaluation_data["logs"] = logs

        # Log operation
        user_id = get_jwt_identity()
        log = OperationLog(
            user_id=user_id,
            operation_type=OperationType.VIEW.value,
            target_type="evaluation",
            target_id=evaluation_id,
            target_description=f"Viewed evaluation {evaluation.evaluation_number}",
            operation_description=f"User viewed evaluation details",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            success=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({"success": True, "data": {"evaluation": evaluation_data}})
    except Exception as e:
        current_app.logger.error(f"Error getting evaluation: {str(e)}")
        return jsonify(
            {"success": False, "message": "Failed to get evaluation", "error": str(e)}
        ), 500


@evaluation_bp.route("", methods=["POST"])
@jwt_required()
def create_evaluation() -> Tuple[Response, int]:
    """Create a new evaluation.
    
    Request Body:
        evaluation_type (str): Type of evaluation ('new_product' or 'mass_production').
        product_name (str): Name of the product.
        part_number (str): Part number.
        start_date (str): Start date in YYYY-MM-DD format.
        expected_end_date (str): Expected end date in YYYY-MM-DD format.
        process_step (str): Process step identifier.
        evaluation_number (str, optional): Unique evaluation number (auto-generated if not provided).
        evaluation_reason (str, optional): Reason for the evaluation.
        description (str, optional): Detailed description.
        status (str, optional): Initial status (defaults to 'draft').
    
    Returns:
        Tuple[Response, int]: JSON response with created evaluation and HTTP status code.
        
    Raises:
        400: If required fields are missing or invalid.
        500: If database operation fails.
    ---
    tags:
      - Evaluations
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - evaluation_type
              - product_name
              - part_number
              - start_date
              - expected_end_date
              - process_step
            properties:
              evaluation_number:
                type: string
                description: Unique evaluation number (auto-generated if not provided)
              evaluation_type:
                type: string
                enum: [new_product, mass_production]
                description: Type of evaluation
              product_name:
                type: string
                description: Name of the product
              part_number:
                type: string
                description: Part number
              evaluation_reason:
                type: string
                description: Reason for the evaluation
              description:
                type: string
                description: Detailed description
              start_date:
                type: string
                format: date
                description: Start date of the evaluation
              expected_end_date:
                type: string
                format: date
                description: Expected end date of the evaluation
              process_step:
                type: string
                description: Process step identifier (e.g., M031)
              status:
                type: string
                enum: [draft, in_progress]
                description: Initial status (defaults to draft)
    responses:
      201:
        description: Evaluation created successfully
      400:
        description: Invalid request data
      401:
        description: Unauthorized
      500:
        description: Internal server error

    """
    try:
        data = request.json
        user_id = get_jwt_identity()

        # Validate required fields (evaluation_number is now optional)
        required_fields = [
            "evaluation_type",
            "product_name",
            "part_number",
            "start_date",
            "expected_end_date",
            "process_step",
        ]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify(
                    {"success": False, "message": f"Missing required field: {field}"}
                ), 400

        # Generate evaluation number if not provided
        evaluation_number = data.get("evaluation_number")
        if not evaluation_number:
            evaluation_number = generate_evaluation_number()

        # Create evaluation
        evaluation = Evaluation(
            evaluation_number=evaluation_number,
            evaluation_type=data["evaluation_type"],
            product_name=data["product_name"],
            part_number=data["part_number"],
            evaluation_reason=data.get("evaluation_reason", ""),
            remarks=data.get("remarks", data.get("description", "")),
            status=data.get("status", EvaluationStatus.DRAFT.value),
            start_date=datetime.strptime(data["start_date"], "%Y-%m-%d").date(),
            expected_end_date=datetime.strptime(
                data["expected_end_date"], "%Y-%m-%d"
            ).date(),
            process_step=data["process_step"],
            evaluator_id=user_id,
            pgm_version=data.get("pgm_version"),
            material_info=data.get("material_info"),
            capacity=data.get("capacity"),
            interface_type=data.get("interface_type"),
            form_factor=data.get("form_factor"),
            temperature_grade=data.get("temperature_grade"),
        )

        db.session.add(evaluation)
        db.session.commit()

        # Log operation
        log = OperationLog(
            user_id=user_id,
            operation_type=OperationType.CREATE.value,
            target_type="evaluation",
            target_id=evaluation.id,
            target_description=f"Created evaluation {evaluation.evaluation_number}",
            operation_description="User created a new evaluation",
            new_data=json.dumps(evaluation.to_dict()),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            success=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Evaluation created successfully",
                "data": {"evaluation": evaluation.to_dict()},
            }
        ), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating evaluation: {str(e)}")
        return jsonify(
            {
                "success": False,
                "message": "Failed to create evaluation",
                "error": str(e),
            }
        ), 500


@evaluation_bp.route("/<int:evaluation_id>", methods=["PUT"])
@jwt_required()
def update_evaluation(evaluation_id: int) -> Tuple[Response, int]:
    """Update an existing evaluation.
    
    Args:
        evaluation_id (int): ID of the evaluation to update.
    
    Request Body:
        product_name (str, optional): Name of the product.
        part_number (str, optional): Part number.
        evaluation_reason (str, optional): Reason for the evaluation.
        description (str, optional): Detailed description.
        expected_end_date (str, optional): Expected end date in YYYY-MM-DD format.
        process_step (str, optional): Process step identifier.
    
    Returns:
        Tuple[Response, int]: JSON response with updated evaluation and HTTP status code.
        
    Raises:
        400: If evaluation cannot be updated due to status constraints.
        403: If user is not authorized to update the evaluation.
        404: If evaluation not found.
        500: If database operation fails.
    ---
    tags:
      - Evaluations
    security:
      - bearerAuth: []
    parameters:
      - name: evaluation_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the evaluation to update
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              product_name:
                type: string
                description: Name of the product
              part_number:
                type: string
                description: Part number
              evaluation_reason:
                type: string
                description: Reason for the evaluation
              description:
                type: string
                description: Detailed description
              expected_end_date:
                type: string
                format: date
                description: Expected end date of the evaluation
              process_step:
                type: string
                description: Process step identifier (e.g., M031)
    responses:
      200:
        description: Evaluation updated successfully
      400:
        description: Invalid request data
      401:
        description: Unauthorized
      404:
        description: Evaluation not found
      500:
        description: Internal server error

    """
    try:
        data = request.json
        user_id = get_jwt_identity()

        evaluation = Evaluation.query.get(evaluation_id)

        if not evaluation:
            return jsonify({"success": False, "message": "Evaluation not found"}), 404

        # Check if user is authorized to update the evaluation
        if evaluation.evaluator_id != user_id and not User.query.get(
            user_id
        ).has_permission("admin"):
            return jsonify(
                {"success": False, "message": "Unauthorized to update this evaluation"}
            ), 403

        # Check if evaluation can be updated
        if evaluation.status not in [
            EvaluationStatus.DRAFT.value,
            EvaluationStatus.IN_PROGRESS.value,
        ]:
            return jsonify(
                {
                    "success": False,
                    "message": f"Cannot update evaluation in {evaluation.status} status",
                }
            ), 400

        # Store old data for logging
        old_data = evaluation.to_dict()

        # Update fields
        if "product_name" in data:
            evaluation.product_name = data["product_name"]
        if "part_number" in data:
            evaluation.part_number = data["part_number"]
        if "evaluation_reason" in data:
            evaluation.evaluation_reason = data["evaluation_reason"]
        if "description" in data or "remarks" in data:
            evaluation.remarks = data.get("remarks", data.get("description", ""))
        if "expected_end_date" in data:
            evaluation.expected_end_date = datetime.strptime(
                data["expected_end_date"], "%Y-%m-%d"
            ).date()
        if "process_step" in data:
            evaluation.process_step = data["process_step"]
        
        # Update technical specifications
        if "pgm_version" in data:
            evaluation.pgm_version = data["pgm_version"]
        if "material_info" in data:
            evaluation.material_info = data["material_info"]
        if "capacity" in data:
            evaluation.capacity = data["capacity"]
        if "interface_type" in data:
            evaluation.interface_type = data["interface_type"]
        if "form_factor" in data:
            evaluation.form_factor = data["form_factor"]
        if "temperature_grade" in data:
            evaluation.temperature_grade = data["temperature_grade"]

        db.session.commit()

        # Log operation
        log = OperationLog(
            user_id=user_id,
            operation_type=OperationType.UPDATE.value,
            target_type="evaluation",
            target_id=evaluation.id,
            target_description=f"Updated evaluation {evaluation.evaluation_number}",
            operation_description="User updated evaluation details",
            old_data=json.dumps(old_data),
            new_data=json.dumps(evaluation.to_dict()),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            success=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Evaluation updated successfully",
                "data": {"evaluation": evaluation.to_dict()},
            }
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating evaluation: {str(e)}")
        return jsonify(
            {
                "success": False,
                "message": "Failed to update evaluation",
                "error": str(e),
            }
        ), 500


@evaluation_bp.route("/<int:evaluation_id>/status", methods=["PUT"])
@jwt_required()
def update_evaluation_status(evaluation_id: int) -> Tuple[Response, int]:
    """Update the status of an evaluation.
    
    Args:
        evaluation_id (int): ID of the evaluation to update.
    
    Request Body:
        status (str): New status for the evaluation.
    
    Returns:
        Tuple[Response, int]: JSON response with updated evaluation and HTTP status code.
        
    Raises:
        400: If status is missing or invalid.
        403: If user is not authorized to update the evaluation status.
        404: If evaluation not found.
        500: If database operation fails.
    ---
    tags:
      - Evaluations
    security:
      - bearerAuth: []
    parameters:
      - name: evaluation_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the evaluation to update
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - status
            properties:
              status:
                type: string
                enum: [draft, in_progress, pending_part_approval, pending_group_approval, completed, paused, cancelled, rejected]
                description: New status for the evaluation
    responses:
      200:
        description: Evaluation status updated successfully
      400:
        description: Invalid request data or status transition
      401:
        description: Unauthorized
      404:
        description: Evaluation not found
      500:
        description: Internal server error

    """
    try:
        data = request.json
        user_id = get_jwt_identity()

        if "status" not in data:
            return jsonify({"success": False, "message": "Status is required"}), 400

        evaluation = Evaluation.query.get(evaluation_id)

        if not evaluation:
            return jsonify({"success": False, "message": "Evaluation not found"}), 404

        # Check if user is authorized to update the status
        user = User.query.get(user_id)
        if evaluation.evaluator_id != user_id and not user.has_permission("admin"):
            return jsonify(
                {
                    "success": False,
                    "message": "Unauthorized to update this evaluation status",
                }
            ), 403

        # Store old data for logging
        old_data = evaluation.to_dict()

        # Update status
        new_status = data["status"]
        evaluation.status = new_status

        # Set actual end date if status is completed
        if new_status == EvaluationStatus.COMPLETED.value:
            evaluation.actual_end_date = datetime.now().date()

        db.session.commit()

        # Log operation
        log = OperationLog(
            user_id=user_id,
            operation_type=OperationType.UPDATE.value,
            target_type="evaluation_status",
            target_id=evaluation.id,
            target_description=f"Updated status of evaluation {evaluation.evaluation_number}",
            operation_description=f"User changed evaluation status from {old_data['status']} to {new_status}",
            old_data=json.dumps({"status": old_data["status"]}),
            new_data=json.dumps({"status": new_status}),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            success=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Evaluation status updated successfully",
                "data": {"evaluation": evaluation.to_dict()},
            }
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating evaluation status: {str(e)}")
        return jsonify(
            {
                "success": False,
                "message": "Failed to update evaluation status",
                "error": str(e),
            }
        ), 500


@evaluation_bp.route("/<int:evaluation_id>/logs", methods=["GET"])
@jwt_required()
def get_evaluation_logs(evaluation_id: int) -> Tuple[Response, int]:
    """Get operation logs for a specific evaluation.
    
    Args:
        evaluation_id (int): ID of the evaluation to get logs for.
    
    Returns:
        Tuple[Response, int]: JSON response with operation logs and HTTP status code.
        
    Raises:
        404: If evaluation not found.
        500: If database operation fails.
    ---
    tags:
      - Evaluations
      - Operation Logs
    security:
      - bearerAuth: []
    parameters:
      - name: evaluation_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the evaluation to get logs for
    responses:
      200:
        description: Operation logs for the evaluation
      401:
        description: Unauthorized
      404:
        description: Evaluation not found
      500:
        description: Internal server error

    """
    try:
        user_id = get_jwt_identity()

        evaluation = Evaluation.query.get(evaluation_id)

        if not evaluation:
            return jsonify({"success": False, "message": "Evaluation not found"}), 404

        # Get operation logs
        logs_query = OperationLog.query.filter_by(
            target_type="evaluation", target_id=evaluation_id
        ).order_by(OperationLog.created_at.desc())

        logs = []
        for log in logs_query.all():
            user = User.query.get(log.user_id)
            log_data = log.to_dict()
            log_data["user_name"] = user.full_name if user else "Unknown"
            logs.append(log_data)

        return jsonify({"success": True, "data": {"logs": logs}})
    except Exception as e:
        current_app.logger.error(f"Error getting evaluation logs: {str(e)}")
        return jsonify(
            {
                "success": False,
                "message": "Failed to get evaluation logs",
                "error": str(e),
            }
        ), 500

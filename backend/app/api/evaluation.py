"""API endpoints for evaluation management."""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import Blueprint, Response, current_app, jsonify, request

from app.models import db
from app.models.evaluation import (
    Evaluation,
    EvaluationProcess,
    EvaluationProcessLot,
    EvaluationProcessRaw,
    EvaluationProcessStep,
    EvaluationStatus,
    EvaluationStepFailure,
    EvaluationStepLot,
    FailCode,
)
from app.models.operation_log import OperationLog, OperationType

evaluation_bp = Blueprint("evaluation", __name__)


def _safe_int(value: object, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _split_legacy_lot_numbers(value: str) -> List[str]:
    if not value:
        return []
    tokens: List[str] = []
    for chunk in re.split(r"[\r\n,;]+", value):
        chunk = chunk.strip()
        if not chunk:
            continue
        if " " in chunk:
            for part in chunk.split():
                part = part.strip()
                if part:
                    tokens.append(part)
        else:
            tokens.append(chunk)
    return tokens


def _dedupe_preserve_order(values: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


STEP_CODE_CANONICAL = {
    "M031": "M031",
    "M033": "M033",
    "M100": "M100",
    "M111": "M111",
    "M130": "M130",
    "AQL": "AQL",
    "BASIC": "Basic",
}


def _canonical_step_code(value: str) -> str:
    candidate = (value or "").strip().upper()
    canonical = STEP_CODE_CANONICAL.get(candidate)
    if not canonical:
        raise ValueError(f"Unsupported step code '{value}'")
    return canonical


def _ensure_fail_code_record(
    code_text: Optional[str],
    provided_id: Optional[int],
    snapshot: Optional[str],
    warnings: List[str],
) -> Optional[FailCode]:
    normalized = (code_text or "").strip().upper()
    if not normalized and not provided_id:
        return None

    fail_code = None
    if provided_id is not None:
        fail_code = FailCode.query.get(provided_id)
        if fail_code and normalized and fail_code.code != normalized:
            warnings.append(
                f"Fail code id {provided_id} does not match provided text '{normalized}', using text value."
            )
            fail_code = None

    if fail_code is None and normalized:
        fail_code = FailCode.query.filter_by(code=normalized).first()

    if fail_code is None and normalized:
        fail_code = FailCode(
            code=normalized,
            short_name=(snapshot or None),
            is_provisional=True,
            source="nested-ui",
        )
        db.session.add(fail_code)
        db.session.flush()
    elif fail_code is not None:
        if snapshot and not fail_code.short_name:
            fail_code.short_name = snapshot
        if not fail_code.source:
            fail_code.source = "nested-ui"

    return fail_code


def _normalize_nested_payload(
    payload: Dict[str, Any],
    warnings: List[str],
) -> Dict[str, Any]:
    lots_input = payload.get("lots")
    legacy_lot_number_raw = str(
        payload.get("legacy_lot_number") or payload.get("lot_number") or ""
    ).strip()
    legacy_quantity_raw = payload.get("legacy_quantity")
    if legacy_quantity_raw is None:
        legacy_quantity_raw = payload.get("quantity")

    normalized_lots: List[Dict[str, Any]] = []
    alias_map: Dict[str, Dict[str, Any]] = {}
    primary_alias_map: Dict[str, Dict[str, Any]] = {}

    if isinstance(lots_input, list) and lots_input:
        for idx, raw_lot in enumerate(lots_input, start=1):
            lot_number = str(raw_lot.get("lot_number") or "").strip()
            if not lot_number:
                raise ValueError(f"Lot {idx} must include lot_number")

            quantity = _safe_int(raw_lot.get("quantity"), default=0)
            alias = str(
                raw_lot.get("temp_id")
                or raw_lot.get("client_id")
                or raw_lot.get("id")
                or f"lot-{idx}"
            )

            entry = {
                "lot_number": lot_number,
                "quantity": quantity,
                "alias": alias,
                "id": raw_lot.get("id"),
            }
            normalized_lots.append(entry)
            primary_alias_map[alias] = entry
            alias_map[str(alias)] = entry
            if raw_lot.get("id") is not None:
                alias_map[str(raw_lot.get("id"))] = entry
            if raw_lot.get("client_id") is not None:
                alias_map[str(raw_lot.get("client_id"))] = entry
    else:
        tokens = _split_legacy_lot_numbers(legacy_lot_number_raw)
        if not tokens:
            raise ValueError("At least one lot is required")

        distribution_total = _safe_int(legacy_quantity_raw, default=0)
        base = distribution_total // len(tokens) if tokens else 0
        remainder = distribution_total - base * len(tokens)

        for idx, token in enumerate(tokens, start=1):
            quantity = base
            if remainder > 0:
                quantity += 1
                remainder -= 1
            alias = f"legacy-{idx}"
            entry = {
                "lot_number": token,
                "quantity": quantity,
                "alias": alias,
                "id": None,
            }
            normalized_lots.append(entry)
            primary_alias_map[alias] = entry
            alias_map[alias] = entry

    if not normalized_lots:
        raise ValueError("At least one lot is required")

    steps_input = payload.get("steps")
    if not isinstance(steps_input, list) or not steps_input:
        raise ValueError("steps array is required")

    all_aliases = [entry["alias"] for entry in normalized_lots]
    normalized_steps: List[Dict[str, Any]] = []

    for idx, raw_step in enumerate(steps_input, start=1):
        canonical_code = _canonical_step_code(raw_step.get("step_code"))
        step_label_value = (raw_step.get("step_label") or "").strip()
        if not step_label_value:
            raise ValueError(f"Step {idx} must include step_label")

        eval_code_raw = (raw_step.get("eval_code") or "").strip()
        eval_code = eval_code_raw.upper() if eval_code_raw else None

        order_index = _safe_int(raw_step.get("order_index"), default=idx)
        notes_value = (raw_step.get("notes") or "").strip() or None

        results_applicable = raw_step.get("results_applicable")
        if results_applicable is None:
            results_applicable = canonical_code not in {"M033", "M100"}
        else:
            results_applicable = bool(results_applicable)

        total_units_manual = bool(raw_step.get("total_units_manual", False))

        lot_refs_raw = raw_step.get("lot_refs")
        mapped_aliases: List[str] = []
        if isinstance(lot_refs_raw, list) and lot_refs_raw:
            for ref in lot_refs_raw:
                entry = alias_map.get(str(ref))
                if not entry:
                    raise ValueError(f"Step {idx} references unknown lot '{ref}'")
                mapped_aliases.append(entry["alias"])
        else:
            mapped_aliases = all_aliases.copy()

        mapped_aliases = _dedupe_preserve_order(mapped_aliases)
        if not mapped_aliases:
            raise ValueError(f"Step {idx} must reference at least one lot")

        lot_quantity_sum = sum(
            primary_alias_map[alias]["quantity"]
            for alias in mapped_aliases
            if alias in primary_alias_map
        )

        failures_input = raw_step.get("failures") or []
        if not isinstance(failures_input, list):
            warnings.append(f"Step {idx} failures data ignored (expected list)")
            failures_input = []

        normalized_failures: List[Dict[str, Any]] = []
        if results_applicable:
            for failure_idx, raw_failure in enumerate(failures_input, start=1):
                fail_code_text = str(raw_failure.get("fail_code_text") or "").strip()
                if not fail_code_text:
                    warnings.append(
                        f"Step {idx} failure {failure_idx}: missing fail_code_text, entry skipped"
                    )
                    continue

                normalized_failures.append(
                    {
                        "sequence": _safe_int(
                            raw_failure.get("sequence"), default=failure_idx
                        ),
                        "serial_number": (
                            raw_failure.get("serial_number") or ""
                        ).strip()
                        or None,
                        "fail_code_id": raw_failure.get("fail_code_id"),
                        "fail_code_text": fail_code_text.upper(),
                        "fail_code_name_snapshot": (
                            raw_failure.get("fail_code_name_snapshot") or ""
                        ).strip()
                        or None,
                        "analysis_result": (
                            raw_failure.get("analysis_result") or ""
                        ).strip()
                        or None,
                    }
                )
        else:
            if failures_input:
                warnings.append(
                    f"Step {idx}: ignoring failures because results_applicable is false"
                )
            normalized_failures = []

        if results_applicable:
            declared_fail_units = raw_step.get("fail_units")
            normalized_fail_units = len(normalized_failures)
            if (
                declared_fail_units is not None
                and _safe_int(declared_fail_units, default=normalized_fail_units)
                != normalized_fail_units
            ):
                warnings.append(
                    f"Step {idx} fail units adjusted to match failure rows ({normalized_fail_units})"
                )

            declared_total_units = raw_step.get("total_units")
            if declared_total_units is None:
                total_units_value = None
            else:
                total_units_value = _safe_int(declared_total_units, default=None)

            if not total_units_manual or total_units_value is None:
                total_units_value = lot_quantity_sum
            elif total_units_value != lot_quantity_sum:
                warnings.append(
                    f"Step {idx} manual total {total_units_value} differs from lot sum {lot_quantity_sum}"
                )

            declared_pass_units = raw_step.get("pass_units")
            if declared_pass_units is None:
                pass_units_value = None
            else:
                pass_units_value = _safe_int(declared_pass_units, default=None)

            if total_units_value is not None:
                if total_units_value < normalized_fail_units:
                    warnings.append(
                        f"Step {idx} total units increased to match failure count ({normalized_fail_units})"
                    )
                    total_units_value = normalized_fail_units

                if pass_units_value is None:
                    pass_units_value = max(total_units_value - normalized_fail_units, 0)

                if total_units_value != (pass_units_value or 0) + normalized_fail_units:
                    warnings.append(
                        f"Step {idx} totals mismatch: total={total_units_value}, pass={pass_units_value}, fail={normalized_fail_units}"
                    )
            else:
                pass_units_value = None

        else:
            total_units_manual = False
            total_units_value = None
            normalized_fail_units = 0
            pass_units_value = None

        normalized_steps.append(
            {
                "order_index": order_index,
                "step_code": canonical_code,
                "step_label": step_label_value,
                "eval_code": eval_code,
                "notes": notes_value,
                "lot_aliases": mapped_aliases,
                "lot_quantity_sum": lot_quantity_sum,
                "results_applicable": results_applicable,
                "total_units_manual": total_units_manual
                if results_applicable
                else False,
                "total_units": total_units_value if results_applicable else None,
                "pass_units": pass_units_value if results_applicable else None,
                "fail_units": normalized_fail_units if results_applicable else None,
                "failures": normalized_failures,
            }
        )

    legacy_lot_number_value = legacy_lot_number_raw or None
    legacy_quantity_value = _safe_int(legacy_quantity_raw, default=None)

    payload_for_storage = {
        "lots": [
            {
                "id": entry["id"],
                "temp_id": entry["alias"],
                "client_id": entry["alias"],
                "lot_number": entry["lot_number"],
                "quantity": entry["quantity"],
            }
            for entry in normalized_lots
        ],
        "steps": [
            {
                "order_index": step["order_index"],
                "step_code": step["step_code"],
                "step_label": step["step_label"],
                "eval_code": step["eval_code"],
                "results_applicable": step["results_applicable"],
                "total_units": step["total_units"],
                "total_units_manual": step["total_units_manual"],
                "pass_units": step["pass_units"],
                "fail_units": step["fail_units"],
                "notes": step["notes"],
                "lot_refs": step["lot_aliases"],
                "failures": step["failures"],
            }
            for step in normalized_steps
        ],
        "legacy_lot_number": legacy_lot_number_value,
        "legacy_quantity": legacy_quantity_value,
    }

    return {
        "payload": payload_for_storage,
        "lots": normalized_lots,
        "steps": normalized_steps,
        "legacy_lot_number": legacy_lot_number_value,
        "legacy_quantity": legacy_quantity_value,
    }


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
def get_evaluations() -> tuple[Response, int]:
    """Get a list of evaluations with optional filtering.

    Query Parameters:
        page (int, optional): Page number for pagination. Defaults to 1.
        per_page (int, optional): Number of items per page. Defaults to 10.
        status (str, optional): Filter by evaluation status.
        evaluation_type (str, optional): Filter by evaluation type.
        product_name (str, optional): Filter by product name (partial match).
        scs_charger_name (str, optional): Filter by SCS Charger name.
        head_office_charger_name (str, optional): Filter by Head Office Charger name.

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
      - name: scs_charger_name
        in: query
        schema:
          type: string
        description: Filter by SCS Charger name (partial match)
      - name: head_office_charger_name
        in: query
        schema:
          type: string
        description: Filter by Head Office Charger name (partial match)
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
        scs_charger_name = request.args.get("scs_charger_name")
        head_office_charger_name = request.args.get("head_office_charger_name")

        # Build query
        query = Evaluation.query

        # Apply filters
        if status:
            query = query.filter(Evaluation.status == status)
        if evaluation_type:
            query = query.filter(Evaluation.evaluation_type == evaluation_type)
        if product_name:
            query = query.filter(Evaluation.product_name.ilike(f"%{product_name}%"))
        if scs_charger_name:
            query = query.filter(
                Evaluation.scs_charger_name.ilike(f"%{scs_charger_name}%")
            )
        if head_office_charger_name:
            query = query.filter(
                Evaluation.head_office_charger_name.ilike(
                    f"%{head_office_charger_name}%"
                )
            )

        # Sorting
        sort_by = request.args.get("sort_by")
        sort_order = request.args.get("sort_order", "desc").lower()
        allowed_sorts = {
            "evaluation_number": Evaluation.evaluation_number,
            "evaluation_type": Evaluation.evaluation_type,
            "product_name": Evaluation.product_name,
            "part_number": Evaluation.part_number,
            "status": Evaluation.status,
            "start_date": Evaluation.start_date,
            "actual_end_date": Evaluation.actual_end_date,
            "scs_charger_name": Evaluation.scs_charger_name,
            "head_office_charger_name": Evaluation.head_office_charger_name,
        }

        if sort_by in allowed_sorts:
            column = allowed_sorts[sort_by]
            if sort_order == "asc":
                query = query.order_by(column.asc(), Evaluation.created_at.desc())
            else:
                query = query.order_by(column.desc(), Evaluation.created_at.desc())
        else:
            query = query.order_by(Evaluation.created_at.desc())

        # Paginate results
        paginated_evaluations = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Format response
        evaluations = []
        for evaluation in paginated_evaluations.items:
            evaluation_data = evaluation.to_dict()
            evaluations.append(evaluation_data)

        # Log operation
        log = OperationLog(
            operation_type=OperationType.VIEW.value,
            target_type="evaluation_list",
            target_id=None,
            target_description="Viewed evaluation list",
            operation_description=f"User viewed evaluation list with filters: {request.args}",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            request_method=request.method,
            request_path=request.path,
            query_string=request.query_string.decode()
            if request.query_string
            else None,
            status_code=200,
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
def get_evaluation(evaluation_id: int) -> tuple[Response, int]:
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

        # Get evaluation data with related entities
        evaluation_data = evaluation.to_dict(include_details=True)

        # Get operation logs
        logs = []
        for log in evaluation.operation_logs:
            logs.append(log.to_dict())

        evaluation_data["logs"] = logs

        # Log operation
        log = OperationLog(
            operation_type=OperationType.VIEW.value,
            target_type="evaluation",
            target_id=evaluation_id,
            target_description=f"Viewed evaluation {evaluation.evaluation_number}",
            operation_description="User viewed evaluation details",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            request_method=request.method,
            request_path=request.path,
            query_string=request.query_string.decode()
            if request.query_string
            else None,
            status_code=200,
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
def create_evaluation() -> tuple[Response, int]:
    """Create a new evaluation.

    Request Body:
        evaluation_type (str): Type of evaluation ('new_product' or 'mass_production').
        product_name (str): Name of the product.
        part_number (str): Part number.
        start_date (str): Start date in YYYY-MM-DD format.
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
              process_step:
                type: string
                description: Process step identifier
                description: Process step identifier (e.g., M031)
              scs_charger_name:
                type: string
                description: Name of the SCS Charger
              head_office_charger_name:
                type: string
                description: Name of the Head Office Charger
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

        # Validate required fields (evaluation_number is now optional)
        required_fields = [
            "evaluation_type",
            "product_name",
            "part_number",
            "start_date",
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
            process_step=data["process_step"],
            scs_charger_name=data.get("scs_charger_name"),
            head_office_charger_name=data.get("head_office_charger_name"),
            pgm_version=data.get("pgm_version"),
            capacity=data.get("capacity"),
            interface_type=data.get("interface_type"),
            form_factor=data.get("form_factor"),
        )

        db.session.add(evaluation)
        db.session.commit()

        # Log operation
        log = OperationLog(
            operation_type=OperationType.CREATE.value,
            target_type="evaluation",
            target_id=evaluation.id,
            target_description=f"Created evaluation {evaluation.evaluation_number}",
            operation_description="User created a new evaluation",
            new_data=json.dumps(evaluation.to_dict()),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            request_method=request.method,
            request_path=request.path,
            query_string=request.query_string.decode()
            if request.query_string
            else None,
            status_code=201,
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
def update_evaluation(evaluation_id: int) -> tuple[Response, int]:
    """Update an existing evaluation.

    Args:
        evaluation_id (int): ID of the evaluation to update.

    Request Body:
        product_name (str, optional): Name of the product.
        part_number (str, optional): Part number.
        evaluation_reason (str, optional): Reason for the evaluation.
        description (str, optional): Detailed description.
        start_date (date, optional): Start date (YYYY-MM-DD).
        actual_end_date|end_date (date, optional): Actual end date (YYYY-MM-DD).
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

              scs_charger_name:
                type: string
                description: Name of the SCS Charger
              head_office_charger_name:
                type: string
                description: Name of the Head Office Charger
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

        evaluation = Evaluation.query.get(evaluation_id)

        if not evaluation:
            return jsonify({"success": False, "message": "Evaluation not found"}), 404

        # Auth removed

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

        # Dates
        if "start_date" in data and data["start_date"]:
            evaluation.start_date = datetime.strptime(
                data["start_date"], "%Y-%m-%d"
            ).date()
        # Accept either 'actual_end_date' or 'end_date'
        end_value = data.get("actual_end_date") or data.get("end_date")
        if end_value is not None:
            evaluation.actual_end_date = (
                datetime.strptime(end_value, "%Y-%m-%d").date() if end_value else None
            )

        if "process_step" in data:
            evaluation.process_step = data["process_step"]

        # Update charger assignments
        if "scs_charger_name" in data:
            evaluation.scs_charger_name = data["scs_charger_name"]
        if "head_office_charger_name" in data:
            evaluation.head_office_charger_name = data["head_office_charger_name"]

        # Update technical specifications
        if "pgm_version" in data:
            evaluation.pgm_version = data["pgm_version"]

        if "capacity" in data:
            evaluation.capacity = data["capacity"]
        if "interface_type" in data:
            evaluation.interface_type = data["interface_type"]
        if "form_factor" in data:
            evaluation.form_factor = data["form_factor"]

        db.session.commit()

        # Log operation
        log = OperationLog(
            operation_type=OperationType.UPDATE.value,
            target_type="evaluation",
            target_id=evaluation.id,
            target_description=f"Updated evaluation {evaluation.evaluation_number}",
            operation_description="User updated evaluation details",
            old_data=json.dumps(old_data),
            new_data=json.dumps(evaluation.to_dict()),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            request_method=request.method,
            request_path=request.path,
            query_string=request.query_string.decode()
            if request.query_string
            else None,
            status_code=200,
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


@evaluation_bp.route("/<int:evaluation_id>/processes/nested", methods=["POST"])
def save_nested_process(evaluation_id: int) -> tuple[Response, int]:
    """Persist nested process data submitted from the new UI."""

    evaluation = Evaluation.query.get(evaluation_id)
    if not evaluation:
        return jsonify({"success": False, "message": "Evaluation not found"}), 404

    payload = request.get_json(silent=True) or {}
    warnings: List[str] = []

    try:
        normalized = _normalize_nested_payload(payload, warnings)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400

    normalized_lots = normalized["lots"]
    normalized_steps = normalized["steps"]
    normalized_payload = normalized["payload"]

    try:
        existing_steps = EvaluationProcessStep.query.filter_by(
            evaluation_id=evaluation.id
        ).all()
        for step in existing_steps:
            db.session.delete(step)

        existing_lots = EvaluationProcessLot.query.filter_by(
            evaluation_id=evaluation.id
        ).all()
        for lot in existing_lots:
            db.session.delete(lot)

        db.session.flush()

        lot_records: List[tuple[str, EvaluationProcessLot]] = []
        for entry in normalized_lots:
            lot_record = EvaluationProcessLot(
                evaluation_id=evaluation.id,
                lot_number=entry["lot_number"],
                quantity=entry["quantity"],
            )
            db.session.add(lot_record)
            lot_records.append((entry["alias"], lot_record))

        db.session.flush()

        alias_to_record: Dict[str, EvaluationProcessLot] = {
            alias: record for alias, record in lot_records
        }

        for step_data in normalized_steps:
            mapped_records = [
                alias_to_record[alias] for alias in step_data["lot_aliases"]
            ]
            lot_quantity_sum = sum(record.quantity for record in mapped_records)
            lot_number_value = (
                mapped_records[0].lot_number if len(mapped_records) == 1 else "MULTI"
            )

            results_applicable = step_data["results_applicable"]
            total_units_value = step_data["total_units"] if results_applicable else None
            pass_units_value = step_data["pass_units"] if results_applicable else None
            fail_units_value = step_data["fail_units"] if results_applicable else None

            step_record = EvaluationProcessStep(
                evaluation_id=evaluation.id,
                lot_number=lot_number_value,
                quantity=lot_quantity_sum,
                order_index=step_data["order_index"],
                step_code=step_data["step_code"],
                step_label=step_data["step_label"],
                eval_code=step_data["eval_code"],
                results_applicable=results_applicable,
                total_units=total_units_value,
                total_units_manual=step_data["total_units_manual"]
                if results_applicable
                else False,
                pass_units=pass_units_value,
                fail_units=fail_units_value,
                notes=step_data["notes"],
            )
            db.session.add(step_record)
            db.session.flush()

            for lot_record in mapped_records:
                db.session.add(
                    EvaluationStepLot(
                        step_id=step_record.id,
                        lot_id=lot_record.id,
                        quantity_override=None,
                    )
                )

            for failure in step_data["failures"]:
                fail_code_record = _ensure_fail_code_record(
                    failure.get("fail_code_text"),
                    failure.get("fail_code_id"),
                    failure.get("fail_code_name_snapshot"),
                    warnings,
                )

                failure_record = EvaluationStepFailure(
                    step_id=step_record.id,
                    sequence=failure.get("sequence"),
                    serial_number=failure.get("serial_number"),
                    fail_code_id=fail_code_record.id if fail_code_record else None,
                    fail_code_text=failure.get("fail_code_text"),
                    fail_code_name_snapshot=failure.get("fail_code_name_snapshot"),
                    analysis_result=failure.get("analysis_result"),
                )
                db.session.add(failure_record)

        raw_record = EvaluationProcessRaw(
            evaluation_id=evaluation.id,
            payload=normalized_payload,
            source="rc0",
        )
        db.session.add(raw_record)

        log = OperationLog(
            operation_type=OperationType.UPDATE.value,
            target_type="evaluation_nested_process",
            target_id=evaluation.id,
            target_description=f"Nested processes updated for {evaluation.evaluation_number}",
            operation_description="Nested process payload saved",
            new_data=normalized_payload,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            request_method=request.method,
            request_path=request.path,
            status_code=200,
            success=True,
        )
        db.session.add(log)

        db.session.commit()

        return jsonify({"success": True, "data": {"warnings": warnings}})
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        current_app.logger.error(
            "Failed to save nested processes for evaluation %s: %s",
            evaluation_id,
            exc,
        )
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Failed to save nested processes",
                    "error": str(exc),
                }
            ),
            500,
        )


@evaluation_bp.route("/<int:evaluation_id>/processes/nested", methods=["GET"])
def get_nested_process(evaluation_id: int) -> tuple[Response, int]:
    """Return the nested process payload for an evaluation."""

    evaluation = Evaluation.query.get(evaluation_id)
    if not evaluation:
        return jsonify({"success": False, "message": "Evaluation not found"}), 404

    lots = (
        EvaluationProcessLot.query.filter_by(evaluation_id=evaluation_id)
        .order_by(EvaluationProcessLot.id.asc())
        .all()
    )
    steps = (
        EvaluationProcessStep.query.filter_by(evaluation_id=evaluation_id)
        .order_by(
            EvaluationProcessStep.order_index.asc(), EvaluationProcessStep.id.asc()
        )
        .all()
    )

    payload_lots: List[Dict[str, Any]] = []
    lot_alias_map: Dict[int, str] = {}
    lot_quantity_map: Dict[int, int] = {}

    for lot in lots:
        alias = f"lot-{lot.id}"
        payload_lots.append(
            {
                "id": lot.id,
                "temp_id": alias,
                "client_id": alias,
                "lot_number": lot.lot_number,
                "quantity": lot.quantity,
            }
        )
        lot_alias_map[lot.id] = alias
        lot_quantity_map[lot.id] = lot.quantity

    fallback_alias_by_label: Dict[str, str] = {}
    fallback_quantity_by_alias: Dict[str, int] = {}
    if not payload_lots and steps:
        for step in steps:
            label = (
                step.lot_number or ""
            ).strip() or f"legacy-{len(fallback_alias_by_label) + 1}"
            if label not in fallback_alias_by_label:
                alias = f"legacy-{len(fallback_alias_by_label) + 1}"
                fallback_alias_by_label[label] = alias
                quantity_value = step.quantity or 0
                payload_lots.append(
                    {
                        "id": None,
                        "temp_id": alias,
                        "client_id": alias,
                        "lot_number": label,
                        "quantity": quantity_value,
                    }
                )
                fallback_quantity_by_alias[alias] = quantity_value

    warnings: List[str] = []
    payload_steps: List[Dict[str, Any]] = []

    for index, step in enumerate(steps, start=1):
        lot_refs: List[str] = []
        if step.lot_assignments:
            lot_refs = _dedupe_preserve_order(
                [
                    lot_alias_map.get(link.lot_id)
                    for link in step.lot_assignments
                    if link.lot_id in lot_alias_map
                ]
            )

        if not lot_refs and fallback_alias_by_label:
            label = (step.lot_number or "").strip()
            alias = fallback_alias_by_label.get(label)
            if alias:
                lot_refs = [alias]

        if not lot_refs and payload_lots:
            lot_refs = [lot["temp_id"] for lot in payload_lots]

        results_applicable = (
            step.results_applicable if step.results_applicable is not None else True
        )
        total_units = step.total_units if step.total_units is not None else None
        pass_units = step.pass_units if step.pass_units is not None else None
        fail_units = step.fail_units if step.fail_units is not None else None

        lot_sum = 0
        if step.lot_assignments:
            lot_sum = sum(
                lot_quantity_map.get(link.lot_id, 0) for link in step.lot_assignments
            )
        elif lot_refs and fallback_quantity_by_alias:
            lot_sum = sum(
                fallback_quantity_by_alias.get(alias, 0) for alias in lot_refs
            )

        if results_applicable:
            if fail_units is None:
                fail_units = len(step.failures or [])
            if total_units is not None and pass_units is not None:
                if total_units != (pass_units or 0) + fail_units:
                    warnings.append(
                        f"Step {index} totals mismatch: total={total_units}, pass={pass_units}, fail={fail_units}"
                    )
            if lot_refs and total_units is not None and total_units != lot_sum:
                warnings.append(
                    f"Step {index} lot quantity mismatch: total_units={total_units}, lot_sum={lot_sum}"
                )
        else:
            total_units = None
            pass_units = None
            fail_units = None

        failures_payload = sorted(
            step.failures, key=lambda failure: failure.sequence or 0
        )
        payload_steps.append(
            {
                "order_index": step.order_index,
                "step_code": step.step_code,
                "step_label": step.step_label,
                "eval_code": step.eval_code,
                "results_applicable": results_applicable,
                "total_units": total_units,
                "total_units_manual": bool(step.total_units_manual)
                if results_applicable
                else False,
                "pass_units": pass_units,
                "fail_units": fail_units,
                "notes": step.notes,
                "lot_refs": lot_refs,
                "failures": [
                    {
                        "sequence": failure.sequence,
                        "serial_number": failure.serial_number,
                        "fail_code_id": failure.fail_code_id,
                        "fail_code_text": failure.fail_code_text,
                        "fail_code_name_snapshot": failure.fail_code_name_snapshot,
                        "analysis_result": failure.analysis_result,
                    }
                    for failure in failures_payload
                ],
            }
        )

    latest_raw = (
        EvaluationProcessRaw.query.filter_by(evaluation_id=evaluation_id)
        .order_by(EvaluationProcessRaw.created_at.desc())
        .first()
    )
    legacy_lot_number = None
    legacy_quantity = None
    if latest_raw and isinstance(latest_raw.payload, dict):
        legacy_lot_number = latest_raw.payload.get("legacy_lot_number")
        legacy_quantity = latest_raw.payload.get("legacy_quantity")

    response_payload = {
        "lots": payload_lots,
        "steps": payload_steps,
        "legacy_lot_number": legacy_lot_number,
        "legacy_quantity": legacy_quantity,
    }

    return jsonify(
        {"success": True, "data": {"payload": response_payload, "warnings": warnings}}
    )


@evaluation_bp.route("/<int:evaluation_id>/processes", methods=["POST"])
def create_evaluation_process(evaluation_id: int) -> tuple[Response, int]:
    """Create a new evaluation process for an evaluation.

    Args:
        evaluation_id (int): ID of the evaluation.

    Request Body:
        title (str, optional): Process title.
        eval_code (str): Evaluation code.
        lot_number (str): Lot number.
        quantity (int): Quantity.
        process_description (str): Process flow description.
        manufacturing_test_results (str, optional): Manufacturing test results.
        defect_analysis_results (str, optional): Defect analysis results.
        aql_result (str, optional): AQL result.

    Returns:
        Tuple[Response, int]: JSON response with created process and HTTP status code.

    Raises:
        400: If required fields are missing or invalid.
        404: If evaluation not found.
        500: If database operation fails.
    ---
    tags:
      - Evaluation Processes
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - eval_code
              - lot_number
              - quantity
              - process_description
            properties:
              eval_code:
                type: string
                description: Evaluation code
              lot_number:
                type: string
                description: Lot number
              quantity:
                type: integer
                description: Quantity
              process_description:
                type: string
                description: Process flow description
              manufacturing_test_results:
                type: string
                description: Manufacturing test results
              defect_analysis_results:
                type: string
                description: Defect analysis results
              aql_result:
                type: string
                description: AQL result
    responses:
      201:
        description: Evaluation process created successfully
      400:
        description: Invalid request data
      404:
        description: Evaluation not found
      500:
        description: Internal server error

    """
    try:
        data = request.json

        # Check if evaluation exists
        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return jsonify({"success": False, "message": "Evaluation not found"}), 404

        # Validate required fields
        required_fields = ["eval_code", "lot_number", "quantity", "process_description"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify(
                    {"success": False, "message": f"Missing required field: {field}"}
                ), 400

        # Create evaluation process
        process = EvaluationProcess(
            evaluation_id=evaluation_id,
            title=data.get("title", ""),
            eval_code=data["eval_code"],
            lot_number=data["lot_number"],
            quantity=data["quantity"],
            process_description=data["process_description"],
            manufacturing_test_results=data.get("manufacturing_test_results"),
            defect_analysis_results=data.get("defect_analysis_results"),
            aql_result=data.get("aql_result"),
        )

        db.session.add(process)
        db.session.commit()

        # Log operation
        log = OperationLog(
            operation_type=OperationType.CREATE.value,
            target_type="evaluation_process",
            target_id=process.id,
            target_description=f"Created process {process.eval_code} for evaluation {evaluation.evaluation_number}",
            operation_description="User created a new evaluation process",
            new_data=json.dumps(process.to_dict()),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            request_method=request.method,
            request_path=request.path,
            query_string=request.query_string.decode()
            if request.query_string
            else None,
            status_code=201,
            success=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Evaluation process created successfully",
                "data": {"process": process.to_dict()},
            }
        ), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating evaluation process: {str(e)}")
        return jsonify(
            {
                "success": False,
                "message": "Failed to create evaluation process",
                "error": str(e),
            }
        ), 500


@evaluation_bp.route("/<int:evaluation_id>/processes", methods=["GET"])
def get_evaluation_processes(evaluation_id: int) -> tuple[Response, int]:
    """Get all processes for an evaluation.

    Args:
        evaluation_id (int): ID of the evaluation.

    Returns:
        Tuple[Response, int]: JSON response with processes list and HTTP status code.

    Raises:
        404: If evaluation not found.
        500: If database operation fails.
    ---
    tags:
      - Evaluation Processes
    security:
      - bearerAuth: []
    parameters:
      - name: evaluation_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the evaluation
    responses:
      200:
        description: List of evaluation processes
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
                    processes:
                      type: array
                      items:
                        type: object
                        properties:
                          id:
                            type: integer
                          eval_code:
                            type: string
                          lot_number:
                            type: string
                          quantity:
                            type: integer
                          process_description:
                            type: string
                          manufacturing_test_results:
                            type: string
                          defect_analysis_results:
                            type: string
                          aql_result:
                            type: string
                          status:
                            type: string
                          created_at:
                            type: string
                            format: date-time
                          updated_at:
                            type: string
                            format: date-time
      404:
        description: Evaluation not found
      500:
        description: Internal server error

    """
    try:
        # Check if evaluation exists
        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return jsonify({"success": False, "message": "Evaluation not found"}), 404

        # Get all processes for this evaluation
        processes = EvaluationProcess.query.filter_by(evaluation_id=evaluation_id).all()

        # Log operation
        log = OperationLog(
            operation_type=OperationType.VIEW.value,
            target_type="evaluation_processes",
            target_id=evaluation_id,
            target_description=f"Viewed processes for evaluation {evaluation.evaluation_number}",
            operation_description="User viewed evaluation processes",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            request_method=request.method,
            request_path=request.path,
            query_string=request.query_string.decode()
            if request.query_string
            else None,
            success=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "data": {
                    "processes": [process.to_dict() for process in processes],
                },
            }
        )
    except Exception as e:
        current_app.logger.error(f"Error getting evaluation processes: {str(e)}")
        return jsonify(
            {
                "success": False,
                "message": "Failed to get evaluation processes",
                "error": str(e),
            }
        ), 500


@evaluation_bp.route("/<int:evaluation_id>/processes/<int:process_id>", methods=["GET"])
def get_evaluation_process(evaluation_id: int, process_id: int) -> tuple[Response, int]:
    """Get details of a specific evaluation process.

    Args:
        evaluation_id (int): ID of the evaluation.
        process_id (int): ID of the process.

    Returns:
        Tuple[Response, int]: JSON response with process details and HTTP status code.

    Raises:
        404: If evaluation or process not found.
        500: If database operation fails.
    ---
    tags:
      - Evaluation Processes
    security:
      - bearerAuth: []
    parameters:
      - name: evaluation_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the evaluation
      - name: process_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the process
    responses:
      200:
        description: Evaluation process details
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
                    process:
                      type: object
                      properties:
                        id:
                          type: integer
                        eval_code:
                          type: string
                        lot_number:
                          type: string
                        quantity:
                          type: integer
                        process_description:
                          type: string
                        manufacturing_test_results:
                          type: string
                        defect_analysis_results:
                          type: string
                        aql_result:
                          type: string
                        status:
                          type: string
                        created_at:
                          type: string
                          format: date-time
                        updated_at:
                          type: string
                          format: date-time
      404:
        description: Evaluation or process not found
      500:
        description: Internal server error

    """
    try:
        # Check if evaluation exists
        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return jsonify({"success": False, "message": "Evaluation not found"}), 404

        # Get the process
        process = EvaluationProcess.query.filter_by(
            id=process_id, evaluation_id=evaluation_id
        ).first()
        if not process:
            return jsonify({"success": False, "message": "Process not found"}), 404

        # Log operation
        log = OperationLog(
            operation_type=OperationType.VIEW.value,
            target_type="evaluation_process",
            target_id=process_id,
            target_description=f"Viewed process {process.eval_code} for evaluation {evaluation.evaluation_number}",
            operation_description="User viewed evaluation process details",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            request_method=request.method,
            request_path=request.path,
            query_string=request.query_string.decode()
            if request.query_string
            else None,
            success=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "data": {"process": process.to_dict()},
            }
        )
    except Exception as e:
        current_app.logger.error(f"Error getting evaluation process: {str(e)}")
        return jsonify(
            {
                "success": False,
                "message": "Failed to get evaluation process",
                "error": str(e),
            }
        ), 500


@evaluation_bp.route("/<int:evaluation_id>/processes/<int:process_id>", methods=["PUT"])
def update_evaluation_process(
    evaluation_id: int, process_id: int
) -> tuple[Response, int]:
    """Update an evaluation process.

    Args:
        evaluation_id (int): ID of the evaluation.
        process_id (int): ID of the process.

    Request Body:
        eval_code (str, optional): Evaluation code.
        lot_number (str, optional): Lot number.
        quantity (int, optional): Quantity.
        process_description (str, optional): Process flow description.
        manufacturing_test_results (str, optional): Manufacturing test results.
        defect_analysis_results (str, optional): Defect analysis results.
        aql_result (str, optional): AQL result.
        status (str, optional): Process status.

    Returns:
        Tuple[Response, int]: JSON response with updated process and HTTP status code.

    Raises:
        404: If evaluation or process not found.
        500: If database operation fails.
    ---
    tags:
      - Evaluation Processes
    security:
      - bearerAuth: []
    parameters:
      - name: evaluation_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the evaluation
      - name: process_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the process
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              eval_code:
                type: string
                description: Evaluation code
              lot_number:
                type: string
                description: Lot number
              quantity:
                type: integer
                description: Quantity
              process_description:
                type: string
                description: Process flow description
              manufacturing_test_results:
                type: string
                description: Manufacturing test results
              defect_analysis_results:
                type: string
                description: Defect analysis results
              aql_result:
                type: string
                description: AQL result
              status:
                type: string
                enum: [pending, in_progress, completed, failed]
                description: Process status
    responses:
      200:
        description: Evaluation process updated successfully
      404:
        description: Evaluation or process not found
      500:
        description: Internal server error

    """
    try:
        data = request.json

        # Check if evaluation exists
        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return jsonify({"success": False, "message": "Evaluation not found"}), 404

        # Get the process
        process = EvaluationProcess.query.filter_by(
            id=process_id, evaluation_id=evaluation_id
        ).first()
        if not process:
            return jsonify({"success": False, "message": "Process not found"}), 404

        # Update process fields
        old_data = process.to_dict()
        update_fields = [
            "title",
            "eval_code",
            "lot_number",
            "quantity",
            "process_description",
            "manufacturing_test_results",
            "defect_analysis_results",
            "aql_result",
            "status",
        ]

        for field in update_fields:
            if field in data:
                setattr(process, field, data[field])

        db.session.commit()

        # Log operation
        log = OperationLog(
            operation_type=OperationType.UPDATE.value,
            target_type="evaluation_process",
            target_id=process_id,
            target_description=f"Updated process {process.eval_code} for evaluation {evaluation.evaluation_number}",
            operation_description="User updated an evaluation process",
            old_data=json.dumps(old_data),
            new_data=json.dumps(process.to_dict()),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            request_method=request.method,
            request_path=request.path,
            query_string=request.query_string.decode()
            if request.query_string
            else None,
            status_code=200,
            success=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Evaluation process updated successfully",
                "data": {"process": process.to_dict()},
            }
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating evaluation process: {str(e)}")
        return jsonify(
            {
                "success": False,
                "message": "Failed to update evaluation process",
                "error": str(e),
            }
        ), 500


@evaluation_bp.route(
    "/<int:evaluation_id>/processes/<int:process_id>", methods=["DELETE"]
)
def delete_evaluation_process(
    evaluation_id: int, process_id: int
) -> tuple[Response, int]:
    """Delete an evaluation process.

    Args:
        evaluation_id (int): ID of the evaluation.
        process_id (int): ID of the process.

    Returns:
        Tuple[Response, int]: JSON response with success message and HTTP status code.

    Raises:
        404: If evaluation or process not found.
        500: If database operation fails.
    ---
    tags:
      - Evaluation Processes
    security:
      - bearerAuth: []
    parameters:
      - name: evaluation_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the evaluation
      - name: process_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the process
    responses:
      200:
        description: Evaluation process deleted successfully
      404:
        description: Evaluation or process not found
      500:
        description: Internal server error

    """
    try:
        # Check if evaluation exists
        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return jsonify({"success": False, "message": "Evaluation not found"}), 404

        # Get the process
        process = EvaluationProcess.query.filter_by(
            id=process_id, evaluation_id=evaluation_id
        ).first()
        if not process:
            return jsonify({"success": False, "message": "Process not found"}), 404

        # Store process data for logging before deletion
        process_data = process.to_dict()

        # Delete the process
        db.session.delete(process)
        db.session.commit()

        # Log operation
        log = OperationLog(
            operation_type=OperationType.DELETE.value,
            target_type="evaluation_process",
            target_id=process_id,
            target_description=f"Deleted process {process_data['eval_code']} for evaluation {evaluation.evaluation_number}",
            operation_description="User deleted an evaluation process",
            old_data=json.dumps(process_data),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            request_method=request.method,
            request_path=request.path,
            query_string=request.query_string.decode()
            if request.query_string
            else None,
            status_code=200,
            success=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Evaluation process deleted successfully",
            }
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting evaluation process: {str(e)}")
        return jsonify(
            {
                "success": False,
                "message": "Failed to delete evaluation process",
                "error": str(e),
            }
        ), 500


@evaluation_bp.route("/<int:evaluation_id>/status", methods=["PUT"])
def update_evaluation_status(evaluation_id: int) -> tuple[Response, int]:
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

        if "status" not in data:
            return jsonify({"success": False, "message": "Status is required"}), 400

        evaluation = Evaluation.query.get(evaluation_id)

        if not evaluation:
            return jsonify({"success": False, "message": "Evaluation not found"}), 404

        # Auth removed

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
            operation_type=OperationType.UPDATE.value,
            target_type="evaluation_status",
            target_id=evaluation.id,
            target_description=f"Updated status of evaluation {evaluation.evaluation_number}",
            operation_description=f"User changed evaluation status from {old_data['status']} to {new_status}",
            old_data=json.dumps({"status": old_data["status"]}),
            new_data=json.dumps({"status": new_status}),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            request_method=request.method,
            request_path=request.path,
            query_string=request.query_string.decode()
            if request.query_string
            else None,
            status_code=200,
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
def get_evaluation_logs(evaluation_id: int) -> tuple[Response, int]:
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
        evaluation = Evaluation.query.get(evaluation_id)

        if not evaluation:
            return jsonify({"success": False, "message": "Evaluation not found"}), 404

        # Collect related process IDs
        process_ids = [
            p.id
            for p in EvaluationProcess.query.with_entities(EvaluationProcess.id)
            .filter_by(evaluation_id=evaluation_id)
            .all()
        ]
        process_ids = (
            [pid for (pid,) in process_ids]
            if process_ids and isinstance(process_ids[0], tuple)
            else process_ids
        )

        # Compose logs across evaluation, status, and processes
        logs = []
        logs += [
            log.to_dict()
            for log in OperationLog.query.filter_by(
                target_type="evaluation", target_id=evaluation_id
            )
            .order_by(OperationLog.created_at.desc())
            .all()
        ]
        logs += [
            log.to_dict()
            for log in OperationLog.query.filter_by(
                target_type="evaluation_status", target_id=evaluation_id
            )
            .order_by(OperationLog.created_at.desc())
            .all()
        ]
        if process_ids:
            logs += [
                log.to_dict()
                for log in OperationLog.query.filter(
                    OperationLog.target_type == "evaluation_process",
                    OperationLog.target_id.in_(process_ids),
                )
                .order_by(OperationLog.created_at.desc())
                .all()
            ]

        # Sort logs by created_at descending
        logs.sort(key=lambda x: x.get("created_at", ""), reverse=True)

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

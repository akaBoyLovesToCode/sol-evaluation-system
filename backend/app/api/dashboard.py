from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional

from flask import Blueprint, request, jsonify, current_app, Response
from flask_jwt_extended import jwt_required
from sqlalchemy import func, and_, or_
from app import db
from app.models import Evaluation, User, Message, OperationLog
from app.utils.decorators import handle_exceptions, cache_response
from app.utils.helpers import create_response, parse_date_string, get_current_user_id

# Create dashboard blueprint
dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/overview", methods=["GET"])
@jwt_required()
@handle_exceptions
def get_dashboard_overview() -> Response:
    """Get dashboard overview statistics.

    Provides comprehensive dashboard data including evaluation counts, status distribution,
    recent evaluations, pending approvals, and user statistics based on user role.

    Returns:
        Response: JSON response containing dashboard overview data including:
            - total_evaluations: Total count of evaluations visible to user
            - status_distribution: Breakdown of evaluations by status
            - type_distribution: Breakdown of evaluations by type
            - recent_evaluations: Last 10 evaluations
            - pending_approvals: Pending evaluations for leaders
            - user_statistics: User stats for admins
            - unread_messages: Count of unread messages
            
    Raises:
        500: If database operation fails.

    """
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)

        # Base query for evaluations (role-based filtering)
        base_query = Evaluation.query
        if not current_user.has_permission("part_leader"):
            # Regular users only see their own evaluations
            base_query = base_query.filter(Evaluation.evaluator_id == current_user_id)

        # Total evaluations count
        total_evaluations = base_query.count()

        # Evaluations by status
        status_counts = db.session.query(
            Evaluation.status, func.count(Evaluation.id).label("count")
        )

        if not current_user.has_permission("part_leader"):
            status_counts = status_counts.filter(
                Evaluation.evaluator_id == current_user_id
            )

        status_counts = status_counts.group_by(Evaluation.status).all()

        status_distribution = {
            "in_progress": 0,
            "pending_part_approval": 0,
            "pending_group_approval": 0,
            "completed": 0,
            "paused": 0,
            "cancelled": 0,
            "rejected": 0,
        }

        for status, count in status_counts:
            status_distribution[status] = count

        # Evaluations by type
        type_counts = db.session.query(
            Evaluation.evaluation_type, func.count(Evaluation.id).label("count")
        )

        if not current_user.has_permission("part_leader"):
            type_counts = type_counts.filter(Evaluation.evaluator_id == current_user_id)

        type_counts = type_counts.group_by(Evaluation.evaluation_type).all()

        type_distribution = {"new_product": 0, "mass_production": 0}

        for eval_type, count in type_counts:
            type_distribution[eval_type] = count

        # Recent evaluations (last 10)
        recent_evaluations_query = base_query.order_by(
            Evaluation.created_at.desc()
        ).limit(10)

        recent_evaluations = []
        for evaluation in recent_evaluations_query:
            eval_dict = evaluation.to_dict()
            eval_dict["evaluator_name"] = evaluation.evaluator.full_name
            recent_evaluations.append(eval_dict)

        # Pending approvals (for leaders)
        pending_approvals = []
        if current_user.has_permission("part_leader"):
            pending_query = Evaluation.query

            if current_user.role == "part_leader":
                pending_query = pending_query.filter(
                    Evaluation.status == "pending_part_approval"
                )
            elif current_user.role == "group_leader":
                pending_query = pending_query.filter(
                    or_(
                        Evaluation.status == "pending_part_approval",
                        Evaluation.status == "pending_group_approval",
                    )
                )
            elif current_user.role == "admin":
                pending_query = pending_query.filter(
                    or_(
                        Evaluation.status == "pending_part_approval",
                        Evaluation.status == "pending_group_approval",
                    )
                )

            for evaluation in pending_query.order_by(
                Evaluation.created_at.desc()
            ).limit(5):
                eval_dict = evaluation.to_dict()
                eval_dict["evaluator_name"] = evaluation.evaluator.full_name
                pending_approvals.append(eval_dict)

        # User statistics (for admins)
        user_stats = {}
        if current_user.has_permission("admin"):
            total_users = User.query.count()
            active_users = User.query.filter_by(is_active=True).count()

            # Users by role
            role_counts = (
                db.session.query(User.role, func.count(User.id).label("count"))
                .group_by(User.role)
                .all()
            )

            role_distribution = {
                "admin": 0,
                "group_leader": 0,
                "part_leader": 0,
                "user": 0,
            }

            for role, count in role_counts:
                role_distribution[role] = count

            user_stats = {
                "total_users": total_users,
                "active_users": active_users,
                "role_distribution": role_distribution,
            }

        # Unread messages count
        unread_messages = Message.query.filter_by(
            recipient_id=current_user_id, is_read=False
        ).count()

        return create_response(
            data={
                "total_evaluations": total_evaluations,
                "status_distribution": status_distribution,
                "type_distribution": type_distribution,
                "recent_evaluations": recent_evaluations,
                "pending_approvals": pending_approvals,
                "user_statistics": user_stats,
                "unread_messages": unread_messages,
            },
            message="Dashboard overview retrieved successfully",
        )

    except Exception as e:
        current_app.logger.error(f"Dashboard overview error: {str(e)}")
        return create_response(
            message="Failed to retrieve dashboard overview", status_code=500
        )


@dashboard_bp.route("/statistics", methods=["GET"])
@jwt_required()
@handle_exceptions
def get_detailed_statistics() -> Response:
    """Get detailed statistics with date range filtering.

    Provides comprehensive analytics including evaluations over time, completion rates,
    product statistics, and evaluator performance metrics.

    Query Parameters:
        start_date (str, optional): Start date for filtering in YYYY-MM-DD format.
        end_date (str, optional): End date for filtering in YYYY-MM-DD format.
        group_by (str, optional): Grouping option ('month', 'week', 'day'). Defaults to 'month'.

    Returns:
        Response: JSON response containing detailed statistics including:
            - date_range: Applied date range and grouping
            - evaluations_over_time: Time series data of evaluation counts
            - completion_rates: Completion rate trends over time
            - product_statistics: Top products by evaluation count
            - evaluator_performance: Performance metrics for evaluators (leaders only)
            
    Raises:
        500: If database operation fails.

    """
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)

        # Get query parameters
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")
        group_by = request.args.get("group_by", "month")

        # Parse dates
        start_date = parse_date_string(start_date_str) if start_date_str else None
        end_date = parse_date_string(end_date_str) if end_date_str else None

        # Default to last 12 months if no dates provided
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).date()
        if not end_date:
            end_date = datetime.now().date()

        # Base query with date filtering
        base_query = Evaluation.query.filter(
            Evaluation.start_date >= start_date, Evaluation.start_date <= end_date
        )

        # Apply role-based filtering
        if not current_user.has_permission("part_leader"):
            base_query = base_query.filter(Evaluation.evaluator_id == current_user_id)

        # Get all evaluations and process in Python
        evaluations = base_query.all()

        # Process data in Python to avoid SQL compatibility issues
        period_counts = {}
        completion_data = {}

        for evaluation in evaluations:
            if not evaluation.start_date:
                continue

            # Format period based on group_by parameter
            if group_by == "month":
                period = evaluation.start_date.strftime("%Y-%m")
            elif group_by == "week":
                year, week, _ = evaluation.start_date.isocalendar()
                period = f"{year}-W{week:02d}"
            else:  # day
                period = evaluation.start_date.strftime("%Y-%m-%d")

            # Count evaluations
            period_counts[period] = period_counts.get(period, 0) + 1

            # Count completions
            if period not in completion_data:
                completion_data[period] = {"total": 0, "completed": 0}
            completion_data[period]["total"] += 1
            if evaluation.status == "completed":
                completion_data[period]["completed"] += 1

        # Convert to expected format
        evaluations_over_time = [
            {"period": period, "count": count}
            for period, count in sorted(period_counts.items())
        ]

        # Calculate completion rates
        completion_rates = []
        for period, data in sorted(completion_data.items()):
            total = data["total"]
            completed = data["completed"]
            rate = (completed / total * 100) if total > 0 else 0
            completion_rates.append(
                {
                    "period": period,
                    "total": total,
                    "completed": completed,
                    "completion_rate": round(rate, 2),
                }
            )

        # Product statistics - simplified
        product_counts = {}
        for evaluation in evaluations:
            product = evaluation.product_name or "Unknown"
            product_counts[product] = product_counts.get(product, 0) + 1

        product_statistics = [
            {"product": product, "count": count}
            for product, count in sorted(
                product_counts.items(), key=lambda x: x[1], reverse=True
            )[:10]
        ]

        # Evaluator performance - simplified for leaders only
        evaluator_performance = []
        if current_user.has_permission("part_leader"):
            evaluator_data = {}
            for evaluation in evaluations:
                evaluator_id = evaluation.evaluator_id
                evaluator_name = (
                    evaluation.evaluator.full_name
                    if evaluation.evaluator
                    else "Unknown"
                )

                if evaluator_id not in evaluator_data:
                    evaluator_data[evaluator_id] = {
                        "name": evaluator_name,
                        "total": 0,
                        "completed": 0,
                        "durations": [],
                    }

                evaluator_data[evaluator_id]["total"] += 1

                if evaluation.status == "completed":
                    evaluator_data[evaluator_id]["completed"] += 1

                    # Calculate duration if both dates exist
                    if evaluation.start_date and evaluation.actual_end_date:
                        duration = (
                            evaluation.actual_end_date - evaluation.start_date
                        ).days
                        evaluator_data[evaluator_id]["durations"].append(duration)

            # Convert to expected format
            for evaluator_id, data in evaluator_data.items():
                total = data["total"]
                completed = data["completed"]
                completion_rate = (completed / total * 100) if total > 0 else 0
                avg_duration = (
                    sum(data["durations"]) / len(data["durations"])
                    if data["durations"]
                    else 0
                )

                evaluator_performance.append(
                    {
                        "evaluator_name": data["name"],
                        "total_evaluations": total,
                        "completed_evaluations": completed,
                        "completion_rate": round(completion_rate, 2),
                        "avg_duration_days": round(avg_duration, 1),
                    }
                )

            # Sort by total evaluations and limit to 10
            evaluator_performance.sort(
                key=lambda x: x["total_evaluations"], reverse=True
            )
            evaluator_performance = evaluator_performance[:10]

        return create_response(
            data={
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "group_by": group_by,
                },
                "evaluations_over_time": evaluations_over_time,
                "completion_rates": completion_rates,
                "product_statistics": product_statistics,
                "evaluator_performance": evaluator_performance,
            },
            message="Detailed statistics retrieved successfully",
        )

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        current_app.logger.error(
            f"Detailed statistics error: {str(e)}\n{error_details}"
        )
        return create_response(
            message=f"Failed to retrieve detailed statistics: {str(e)}", status_code=500
        )


@dashboard_bp.route("/reports/evaluation-status", methods=["GET"])
@jwt_required()
@handle_exceptions
def get_evaluation_status_report() -> Response:
    """Get evaluation status report for management.

    Provides detailed breakdown of evaluation statuses with trends and aging analysis.
    Only accessible to users with part_leader permission or higher.

    Returns:
        Response: JSON response containing status report data including:
            - current_status_distribution: Current status breakdown with percentages
            - previous_period_comparison: Status distribution from last 30 days
            - pending_evaluations: List of pending evaluations with age
            - overdue_count: Count of evaluations overdue (>30 days)
            - summary: High-level metrics for quick overview
            
    Raises:
        403: If user lacks required permissions.
        500: If database operation fails.

    """
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)

        # Only leaders and admins can access this report
        if not current_user.has_permission("part_leader"):
            return create_response(message="Permission denied", status_code=403)

        # Current status distribution
        current_status = (
            db.session.query(
                Evaluation.status,
                func.count(Evaluation.id).label("count"),
                func.round(
                    func.count(Evaluation.id)
                    * 100.0
                    / func.sum(func.count(Evaluation.id)).over(),
                    2,
                ).label("percentage"),
            )
            .group_by(Evaluation.status)
            .all()
        )

        # Status distribution for last 30 days (for comparison)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        previous_status = (
            db.session.query(
                Evaluation.status, func.count(Evaluation.id).label("count")
            )
            .filter(Evaluation.created_at >= thirty_days_ago)
            .group_by(Evaluation.status)
            .all()
        )

        # Pending evaluations by age
        pending_evaluations = (
            db.session.query(
                Evaluation.id,
                Evaluation.evaluation_number,
                Evaluation.product_name,
                Evaluation.status,
                User.full_name.label("evaluator_name"),
                func.datediff(func.current_date(), Evaluation.start_date).label(
                    "days_pending"
                ),
            )
            .join(User, Evaluation.evaluator_id == User.id)
            .filter(
                Evaluation.status.in_(
                    ["in_progress", "pending_part_approval", "pending_group_approval"]
                )
            )
            .order_by(func.datediff(func.current_date(), Evaluation.start_date).desc())
            .limit(20)
            .all()
        )

        # Overdue evaluations (more than 30 days)
        overdue_count = (
            db.session.query(func.count(Evaluation.id))
            .filter(
                Evaluation.status.in_(
                    ["in_progress", "pending_part_approval", "pending_group_approval"]
                ),
                func.datediff(func.current_date(), Evaluation.start_date) > 30,
            )
            .scalar()
        )

        return create_response(
            data={
                "current_status_distribution": [
                    {"status": status, "count": count, "percentage": float(percentage)}
                    for status, count, percentage in current_status
                ],
                "previous_period_comparison": [
                    {"status": status, "count": count}
                    for status, count in previous_status
                ],
                "pending_evaluations": [
                    {
                        "id": eval_id,
                        "evaluation_number": eval_number,
                        "product_name": product,
                        "status": status,
                        "evaluator_name": evaluator,
                        "days_pending": days_pending,
                    }
                    for eval_id, eval_number, product, status, evaluator, days_pending in pending_evaluations
                ],
                "overdue_count": overdue_count,
                "summary": {
                    "total_active": sum(
                        count
                        for _, count, _ in current_status
                        if _
                        in [
                            "in_progress",
                            "pending_part_approval",
                            "pending_group_approval",
                        ]
                    ),
                    "total_completed": sum(
                        count for _, count, _ in current_status if _ == "completed"
                    ),
                    "needs_attention": overdue_count,
                },
            },
            message="Evaluation status report retrieved successfully",
        )

    except Exception as e:
        current_app.logger.error(f"Evaluation status report error: {str(e)}")
        return create_response(
            message="Failed to retrieve evaluation status report", status_code=500
        )


@dashboard_bp.route("/reports/productivity", methods=["GET"])
@jwt_required()
@handle_exceptions
def get_productivity_report() -> Response:
    """Get productivity report showing evaluation throughput and efficiency.

    Provides comprehensive productivity analytics including monthly trends,
    top performer rankings, and department comparisons.
    Only accessible to users with part_leader permission or higher.

    Returns:
        Response: JSON response containing productivity data including:
            - monthly_productivity: Monthly evaluation throughput for last 12 months
            - top_performers: Ranking of evaluators by completion rate
            - department_performance: Department-level productivity metrics
            
    Raises:
        403: If user lacks required permissions.
        500: If database operation fails.

    """
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)

        # Only leaders and admins can access this report
        if not current_user.has_permission("part_leader"):
            return create_response(message="Permission denied", status_code=403)

        # Monthly productivity for last 12 months
        twelve_months_ago = datetime.now() - timedelta(days=365)

        monthly_productivity = (
            db.session.query(
                func.date_format(Evaluation.start_date, "%Y-%m").label("month"),
                func.count(Evaluation.id).label("started"),
                func.sum(
                    func.case([(Evaluation.status == "completed", 1)], else_=0)
                ).label("completed"),
                func.avg(
                    func.case(
                        [
                            (
                                and_(
                                    Evaluation.status == "completed",
                                    Evaluation.actual_end_date.isnot(None),
                                ),
                                func.datediff(
                                    Evaluation.actual_end_date, Evaluation.start_date
                                ),
                            )
                        ],
                        else_=None,
                    )
                ).label("avg_completion_time"),
            )
            .filter(Evaluation.start_date >= twelve_months_ago.date())
            .group_by(func.date_format(Evaluation.start_date, "%Y-%m"))
            .order_by(func.date_format(Evaluation.start_date, "%Y-%m"))
            .all()
        )

        # Top performers (evaluators with highest completion rates)
        top_performers = (
            db.session.query(
                User.full_name,
                User.department,
                func.count(Evaluation.id).label("total_evaluations"),
                func.sum(
                    func.case([(Evaluation.status == "completed", 1)], else_=0)
                ).label("completed_evaluations"),
                func.avg(
                    func.case(
                        [
                            (
                                and_(
                                    Evaluation.status == "completed",
                                    Evaluation.actual_end_date.isnot(None),
                                ),
                                func.datediff(
                                    Evaluation.actual_end_date, Evaluation.start_date
                                ),
                            )
                        ],
                        else_=None,
                    )
                ).label("avg_completion_time"),
            )
            .join(User, Evaluation.evaluator_id == User.id)
            .filter(Evaluation.start_date >= twelve_months_ago.date())
            .group_by(User.id, User.full_name, User.department)
            .having(
                func.count(Evaluation.id) >= 3  # At least 3 evaluations
            )
            .order_by(
                (
                    func.sum(
                        func.case([(Evaluation.status == "completed", 1)], else_=0)
                    )
                    / func.count(Evaluation.id)
                ).desc()
            )
            .limit(10)
            .all()
        )

        # Department performance
        department_performance = (
            db.session.query(
                User.department,
                func.count(Evaluation.id).label("total_evaluations"),
                func.sum(
                    func.case([(Evaluation.status == "completed", 1)], else_=0)
                ).label("completed_evaluations"),
                func.avg(
                    func.case(
                        [
                            (
                                and_(
                                    Evaluation.status == "completed",
                                    Evaluation.actual_end_date.isnot(None),
                                ),
                                func.datediff(
                                    Evaluation.actual_end_date, Evaluation.start_date
                                ),
                            )
                        ],
                        else_=None,
                    )
                ).label("avg_completion_time"),
            )
            .join(User, Evaluation.evaluator_id == User.id)
            .filter(
                Evaluation.start_date >= twelve_months_ago.date(),
                User.department.isnot(None),
            )
            .group_by(User.department)
            .order_by(func.count(Evaluation.id).desc())
            .all()
        )

        return create_response(
            data={
                "monthly_productivity": [
                    {
                        "month": month,
                        "started": started,
                        "completed": completed,
                        "completion_rate": round(
                            (completed / started * 100) if started > 0 else 0, 2
                        ),
                        "avg_completion_time": round(float(avg_time or 0), 1),
                    }
                    for month, started, completed, avg_time in monthly_productivity
                ],
                "top_performers": [
                    {
                        "name": name,
                        "department": department,
                        "total_evaluations": total,
                        "completed_evaluations": completed,
                        "completion_rate": round(
                            (completed / total * 100) if total > 0 else 0, 2
                        ),
                        "avg_completion_time": round(float(avg_time or 0), 1),
                    }
                    for name, department, total, completed, avg_time in top_performers
                ],
                "department_performance": [
                    {
                        "department": department,
                        "total_evaluations": total,
                        "completed_evaluations": completed,
                        "completion_rate": round(
                            (completed / total * 100) if total > 0 else 0, 2
                        ),
                        "avg_completion_time": round(float(avg_time or 0), 1),
                    }
                    for department, total, completed, avg_time in department_performance
                ],
            },
            message="Productivity report retrieved successfully",
        )

    except Exception as e:
        current_app.logger.error(f"Productivity report error: {str(e)}")
        return create_response(
            message="Failed to retrieve productivity report", status_code=500
        )

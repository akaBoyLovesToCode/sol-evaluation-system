from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from app import db
from app.models import Evaluation, User, Message, OperationLog
from app.utils.decorators import handle_exceptions, cache_response
from app.utils.helpers import create_response, parse_date_string, get_current_user_id

# Create dashboard blueprint
dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/overview", methods=["GET"])
@jwt_required()
@handle_exceptions
def get_dashboard_overview():
    """
    Get dashboard overview statistics

    Returns:
    - Total evaluations count
    - Evaluations by status
    - Recent evaluations
    - Pending approvals (for leaders)
    - User statistics (for admins)
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
def get_detailed_statistics():
    """
    Get detailed statistics with date range filtering

    Query parameters:
    - start_date: Start date for filtering (YYYY-MM-DD)
    - end_date: End date for filtering (YYYY-MM-DD)
    - group_by: Grouping option ('month', 'week', 'day')
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

        # Evaluations over time
        if group_by == "month":
            date_format = "%Y-%m"
            date_trunc = func.date_format(Evaluation.start_date, "%Y-%m")
        elif group_by == "week":
            date_format = "%Y-W%u"
            date_trunc = func.date_format(Evaluation.start_date, "%Y-W%u")
        else:  # day
            date_format = "%Y-%m-%d"
            date_trunc = func.date_format(Evaluation.start_date, "%Y-%m-%d")

        evaluations_over_time = db.session.query(
            date_trunc.label("period"), func.count(Evaluation.id).label("count")
        ).filter(Evaluation.start_date >= start_date, Evaluation.start_date <= end_date)

        if not current_user.has_permission("part_leader"):
            evaluations_over_time = evaluations_over_time.filter(
                Evaluation.evaluator_id == current_user_id
            )

        evaluations_over_time = (
            evaluations_over_time.group_by(date_trunc).order_by(date_trunc).all()
        )

        # Completion rate over time
        completion_rate_data = db.session.query(
            date_trunc.label("period"),
            func.count(Evaluation.id).label("total"),
            func.sum(func.case([(Evaluation.status == "completed", 1)], else_=0)).label(
                "completed"
            ),
        ).filter(Evaluation.start_date >= start_date, Evaluation.start_date <= end_date)

        if not current_user.has_permission("part_leader"):
            completion_rate_data = completion_rate_data.filter(
                Evaluation.evaluator_id == current_user_id
            )

        completion_rate_data = (
            completion_rate_data.group_by(date_trunc).order_by(date_trunc).all()
        )

        # Calculate completion rates
        completion_rates = []
        for period, total, completed in completion_rate_data:
            rate = (completed / total * 100) if total > 0 else 0
            completion_rates.append(
                {
                    "period": period,
                    "total": total,
                    "completed": completed,
                    "completion_rate": round(rate, 2),
                }
            )

        # Product statistics
        product_stats = db.session.query(
            Evaluation.product_name, func.count(Evaluation.id).label("count")
        ).filter(Evaluation.start_date >= start_date, Evaluation.start_date <= end_date)

        if not current_user.has_permission("part_leader"):
            product_stats = product_stats.filter(
                Evaluation.evaluator_id == current_user_id
            )

        product_stats = (
            product_stats.group_by(Evaluation.product_name)
            .order_by(func.count(Evaluation.id).desc())
            .limit(10)
            .all()
        )

        # Evaluator performance (for leaders)
        evaluator_performance = []
        if current_user.has_permission("part_leader"):
            evaluator_stats = (
                db.session.query(
                    User.full_name,
                    func.count(Evaluation.id).label("total_evaluations"),
                    func.sum(
                        func.case([(Evaluation.status == "completed", 1)], else_=0)
                    ).label("completed_evaluations"),
                    func.avg(
                        func.datediff(
                            func.coalesce(
                                Evaluation.completion_date, func.current_date()
                            ),
                            Evaluation.start_date,
                        )
                    ).label("avg_duration"),
                )
                .join(User, Evaluation.evaluator_id == User.id)
                .filter(
                    Evaluation.start_date >= start_date,
                    Evaluation.start_date <= end_date,
                )
                .group_by(User.id, User.full_name)
                .order_by(func.count(Evaluation.id).desc())
                .limit(10)
                .all()
            )

            for name, total, completed, avg_duration in evaluator_stats:
                completion_rate = (completed / total * 100) if total > 0 else 0
                evaluator_performance.append(
                    {
                        "evaluator_name": name,
                        "total_evaluations": total,
                        "completed_evaluations": completed,
                        "completion_rate": round(completion_rate, 2),
                        "avg_duration_days": round(float(avg_duration or 0), 1),
                    }
                )

        return create_response(
            data={
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "group_by": group_by,
                },
                "evaluations_over_time": [
                    {"period": period, "count": count}
                    for period, count in evaluations_over_time
                ],
                "completion_rates": completion_rates,
                "product_statistics": [
                    {"product": product, "count": count}
                    for product, count in product_stats
                ],
                "evaluator_performance": evaluator_performance,
            },
            message="Detailed statistics retrieved successfully",
        )

    except Exception as e:
        current_app.logger.error(f"Detailed statistics error: {str(e)}")
        return create_response(
            message="Failed to retrieve detailed statistics", status_code=500
        )


@dashboard_bp.route("/reports/evaluation-status", methods=["GET"])
@jwt_required()
@handle_exceptions
def get_evaluation_status_report():
    """
    Get evaluation status report for management

    Returns detailed breakdown of evaluation statuses with trends
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
def get_productivity_report():
    """
    Get productivity report showing evaluation throughput and efficiency
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
                                    Evaluation.completion_date.isnot(None),
                                ),
                                func.datediff(
                                    Evaluation.completion_date, Evaluation.start_date
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
                                    Evaluation.completion_date.isnot(None),
                                ),
                                func.datediff(
                                    Evaluation.completion_date, Evaluation.start_date
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
                                    Evaluation.completion_date.isnot(None),
                                ),
                                func.datediff(
                                    Evaluation.completion_date, Evaluation.start_date
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

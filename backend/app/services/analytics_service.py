"""
Analytics Service for Product Evaluation System

This service handles statistical analysis and data visualization as specified
in Phase 3 requirements. Provides data for charts, reports, and analytics.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func, extract, desc
from flask import current_app
from app import db
from app.models.evaluation import Evaluation, EvaluationStatus, EvaluationType
from app.models.user import User, UserRole
from app.models.operation_log import OperationLog, OperationType
import json


class AnalyticsService:
    """
    Service class for analytics and statistical analysis

    Handles:
    - Statistical analysis of evaluations
    - Data visualization preparation
    - Performance metrics
    - Trend analysis
    """

    @staticmethod
    def get_evaluation_statistics(
        start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get comprehensive evaluation statistics

        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering

        Returns:
            Dictionary with evaluation statistics
        """
        try:
            # Set default date range if not provided (last 12 months)
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=365)

            # Base query with date filtering
            base_query = Evaluation.query.filter(
                and_(
                    Evaluation.created_at >= start_date,
                    Evaluation.created_at <= end_date,
                )
            )

            stats = {}

            # Total evaluations
            stats["total_evaluations"] = base_query.count()

            # Evaluations by status
            status_counts = {}
            for status in EvaluationStatus:
                count = base_query.filter_by(status=status).count()
                status_counts[status.value.lower()] = count
            stats["status_distribution"] = status_counts

            # Evaluations by type
            type_counts = {}
            for eval_type in EvaluationType:
                count = base_query.filter_by(evaluation_type=eval_type).count()
                type_counts[eval_type.value.lower().replace(" ", "_")] = count
            stats["type_distribution"] = type_counts

            # Completion rate
            completed_count = base_query.filter_by(
                status=EvaluationStatus.COMPLETED
            ).count()
            stats["completion_rate"] = round(
                (completed_count / stats["total_evaluations"] * 100)
                if stats["total_evaluations"] > 0
                else 0,
                2,
            )

            # Average completion time
            completed_evals = base_query.filter(
                and_(
                    Evaluation.status == EvaluationStatus.COMPLETED,
                    Evaluation.completed_at.isnot(None),
                )
            ).all()

            if completed_evals:
                total_days = sum(
                    [
                        (eval.completed_at - eval.created_at).days
                        for eval in completed_evals
                    ]
                )
                stats["average_completion_days"] = round(
                    total_days / len(completed_evals), 1
                )
            else:
                stats["average_completion_days"] = 0

            # Overdue evaluations
            overdue_count = base_query.filter(
                and_(
                    Evaluation.due_date < datetime.utcnow().date(),
                    Evaluation.status != EvaluationStatus.COMPLETED,
                )
            ).count()
            stats["overdue_count"] = overdue_count
            stats["overdue_rate"] = round(
                (overdue_count / stats["total_evaluations"] * 100)
                if stats["total_evaluations"] > 0
                else 0,
                2,
            )

            return stats

        except Exception as e:
            current_app.logger.error(f"Error getting evaluation statistics: {str(e)}")
            return {}

    @staticmethod
    def get_monthly_trends(months: int = 12) -> Dict:
        """
        Get monthly trends for evaluations

        Args:
            months: Number of months to analyze

        Returns:
            Dictionary with monthly trend data
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=months * 30)

            # Query evaluations by month
            monthly_data = (
                db.session.query(
                    extract("year", Evaluation.created_at).label("year"),
                    extract("month", Evaluation.created_at).label("month"),
                    func.count(Evaluation.id).label("total"),
                    func.sum(
                        func.case(
                            [(Evaluation.status == EvaluationStatus.COMPLETED, 1)],
                            else_=0,
                        )
                    ).label("completed"),
                    func.sum(
                        func.case(
                            [(Evaluation.status == EvaluationStatus.REJECTED, 1)],
                            else_=0,
                        )
                    ).label("rejected"),
                )
                .filter(Evaluation.created_at >= start_date)
                .group_by(
                    extract("year", Evaluation.created_at),
                    extract("month", Evaluation.created_at),
                )
                .order_by(
                    extract("year", Evaluation.created_at),
                    extract("month", Evaluation.created_at),
                )
                .all()
            )

            # Format data for charts
            labels = []
            total_counts = []
            completed_counts = []
            rejected_counts = []
            completion_rates = []

            for row in monthly_data:
                month_label = f"{int(row.year)}-{int(row.month):02d}"
                labels.append(month_label)
                total_counts.append(row.total)
                completed_counts.append(row.completed or 0)
                rejected_counts.append(row.rejected or 0)

                # Calculate completion rate
                completion_rate = round(
                    (row.completed / row.total * 100) if row.total > 0 else 0, 1
                )
                completion_rates.append(completion_rate)

            return {
                "labels": labels,
                "total_evaluations": total_counts,
                "completed_evaluations": completed_counts,
                "rejected_evaluations": rejected_counts,
                "completion_rates": completion_rates,
            }

        except Exception as e:
            current_app.logger.error(f"Error getting monthly trends: {str(e)}")
            return {}

    @staticmethod
    def get_user_performance_metrics() -> List[Dict]:
        """
        Get performance metrics for all users

        Returns:
            List of user performance dictionaries
        """
        try:
            # Get all active users with evaluation assignments
            users = User.query.filter_by(is_active=True).all()

            performance_data = []

            for user in users:
                # Get user's evaluation statistics
                assigned_evals = Evaluation.query.filter_by(assigned_to=user.id).all()
                created_evals = Evaluation.query.filter_by(created_by=user.id).all()

                # Calculate metrics
                total_assigned = len(assigned_evals)
                completed_assigned = len(
                    [
                        e
                        for e in assigned_evals
                        if e.status == EvaluationStatus.COMPLETED
                    ]
                )
                overdue_assigned = len(
                    [
                        e
                        for e in assigned_evals
                        if e.due_date
                        and e.due_date < datetime.utcnow().date()
                        and e.status != EvaluationStatus.COMPLETED
                    ]
                )

                # Average completion time for completed evaluations
                completed_with_time = [
                    e
                    for e in assigned_evals
                    if e.status == EvaluationStatus.COMPLETED and e.completed_at
                ]

                avg_completion_days = 0
                if completed_with_time:
                    total_days = sum(
                        [
                            (eval.completed_at - eval.created_at).days
                            for eval in completed_with_time
                        ]
                    )
                    avg_completion_days = round(
                        total_days / len(completed_with_time), 1
                    )

                performance_data.append(
                    {
                        "user_id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role.value,
                        "total_assigned": total_assigned,
                        "completed_assigned": completed_assigned,
                        "overdue_assigned": overdue_assigned,
                        "completion_rate": round(
                            (completed_assigned / total_assigned * 100)
                            if total_assigned > 0
                            else 0,
                            1,
                        ),
                        "average_completion_days": avg_completion_days,
                        "total_created": len(created_evals),
                        "last_activity": user.last_login.isoformat()
                        if user.last_login
                        else None,
                    }
                )

            # Sort by completion rate descending
            performance_data.sort(key=lambda x: x["completion_rate"], reverse=True)

            return performance_data

        except Exception as e:
            current_app.logger.error(
                f"Error getting user performance metrics: {str(e)}"
            )
            return []

    @staticmethod
    def get_evaluation_type_analysis() -> Dict:
        """
        Get detailed analysis by evaluation type

        Returns:
            Dictionary with evaluation type analysis
        """
        try:
            analysis = {}

            for eval_type in EvaluationType:
                type_evals = Evaluation.query.filter_by(evaluation_type=eval_type).all()

                if not type_evals:
                    continue

                # Calculate metrics for this type
                total_count = len(type_evals)
                completed_count = len(
                    [e for e in type_evals if e.status == EvaluationStatus.COMPLETED]
                )
                rejected_count = len(
                    [e for e in type_evals if e.status == EvaluationStatus.REJECTED]
                )

                # Average completion time
                completed_with_time = [
                    e
                    for e in type_evals
                    if e.status == EvaluationStatus.COMPLETED and e.completed_at
                ]

                avg_completion_days = 0
                if completed_with_time:
                    total_days = sum(
                        [
                            (eval.completed_at - eval.created_at).days
                            for eval in completed_with_time
                        ]
                    )
                    avg_completion_days = round(
                        total_days / len(completed_with_time), 1
                    )

                # Success rate (completed / (completed + rejected))
                total_finished = completed_count + rejected_count
                success_rate = round(
                    (completed_count / total_finished * 100)
                    if total_finished > 0
                    else 0,
                    1,
                )

                analysis[eval_type.value.lower().replace(" ", "_")] = {
                    "total_count": total_count,
                    "completed_count": completed_count,
                    "rejected_count": rejected_count,
                    "in_progress_count": total_count - completed_count - rejected_count,
                    "completion_rate": round((completed_count / total_count * 100), 1),
                    "success_rate": success_rate,
                    "average_completion_days": avg_completion_days,
                }

            return analysis

        except Exception as e:
            current_app.logger.error(
                f"Error getting evaluation type analysis: {str(e)}"
            )
            return {}

    @staticmethod
    def get_workflow_bottlenecks() -> Dict:
        """
        Identify workflow bottlenecks and delays

        Returns:
            Dictionary with bottleneck analysis
        """
        try:
            bottlenecks = {}

            # Analyze time spent in each status
            status_times = {}

            for status in EvaluationStatus:
                if status == EvaluationStatus.COMPLETED:
                    continue

                # Get evaluations currently in this status
                current_in_status = Evaluation.query.filter_by(status=status).all()

                if current_in_status:
                    total_days = sum(
                        [
                            (datetime.utcnow() - eval.created_at).days
                            for eval in current_in_status
                        ]
                    )
                    avg_days = round(total_days / len(current_in_status), 1)

                    status_times[status.value.lower()] = {
                        "count": len(current_in_status),
                        "average_days": avg_days,
                        "max_days": max(
                            [
                                (datetime.utcnow() - eval.created_at).days
                                for eval in current_in_status
                            ]
                        ),
                    }

            bottlenecks["status_analysis"] = status_times

            # Find evaluations stuck in approval process
            stuck_pending = Evaluation.query.filter(
                and_(
                    Evaluation.status == EvaluationStatus.PENDING,
                    Evaluation.created_at < datetime.utcnow() - timedelta(days=7),
                )
            ).count()

            stuck_in_progress = Evaluation.query.filter(
                and_(
                    Evaluation.status == EvaluationStatus.IN_PROGRESS,
                    Evaluation.created_at < datetime.utcnow() - timedelta(days=14),
                )
            ).count()

            bottlenecks["stuck_evaluations"] = {
                "pending_over_7_days": stuck_pending,
                "in_progress_over_14_days": stuck_in_progress,
            }

            # Identify users with high workload
            user_workloads = (
                db.session.query(
                    User.id,
                    User.username,
                    func.count(Evaluation.id).label("active_count"),
                )
                .join(Evaluation, Evaluation.assigned_to == User.id)
                .filter(
                    Evaluation.status.in_(
                        [EvaluationStatus.PENDING, EvaluationStatus.IN_PROGRESS]
                    )
                )
                .group_by(User.id, User.username)
                .order_by(desc("active_count"))
                .limit(10)
                .all()
            )

            bottlenecks["high_workload_users"] = [
                {
                    "user_id": row.id,
                    "username": row.username,
                    "active_evaluations": row.active_count,
                }
                for row in user_workloads
            ]

            return bottlenecks

        except Exception as e:
            current_app.logger.error(f"Error getting workflow bottlenecks: {str(e)}")
            return {}

    @staticmethod
    def generate_dashboard_data() -> Dict:
        """
        Generate comprehensive dashboard data

        Returns:
            Dictionary with all dashboard data
        """
        try:
            dashboard_data = {}

            # Key metrics
            dashboard_data["key_metrics"] = AnalyticsService.get_evaluation_statistics()

            # Monthly trends (last 6 months)
            dashboard_data["monthly_trends"] = AnalyticsService.get_monthly_trends(6)

            # Evaluation type distribution
            dashboard_data["type_analysis"] = (
                AnalyticsService.get_evaluation_type_analysis()
            )

            # Workflow bottlenecks
            dashboard_data["bottlenecks"] = AnalyticsService.get_workflow_bottlenecks()

            # Recent activity (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_stats = AnalyticsService.get_evaluation_statistics(thirty_days_ago)
            dashboard_data["recent_activity"] = recent_stats

            # Top performers (last 30 days)
            all_performance = AnalyticsService.get_user_performance_metrics()
            dashboard_data["top_performers"] = all_performance[:5]  # Top 5

            return dashboard_data

        except Exception as e:
            current_app.logger.error(f"Error generating dashboard data: {str(e)}")
            return {}

    @staticmethod
    def export_analytics_data(
        start_date: datetime, end_date: datetime, format_type: str = "json"
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Export analytics data for reporting

        Args:
            start_date: Start date for data export
            end_date: End date for data export
            format_type: Export format ('json', 'csv')

        Returns:
            Tuple of (success: bool, message: str, data: Optional[str])
        """
        try:
            # Get comprehensive analytics data
            export_data = {
                "export_info": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "format": format_type,
                },
                "statistics": AnalyticsService.get_evaluation_statistics(
                    start_date, end_date
                ),
                "monthly_trends": AnalyticsService.get_monthly_trends(12),
                "user_performance": AnalyticsService.get_user_performance_metrics(),
                "type_analysis": AnalyticsService.get_evaluation_type_analysis(),
                "bottlenecks": AnalyticsService.get_workflow_bottlenecks(),
            }

            if format_type.lower() == "json":
                return (
                    True,
                    "Data exported successfully",
                    json.dumps(export_data, indent=2),
                )
            elif format_type.lower() == "csv":
                # For CSV, we'll export a simplified version
                csv_data = AnalyticsService._convert_to_csv(export_data)
                return True, "Data exported successfully", csv_data
            else:
                return False, f"Unsupported format: {format_type}", None

        except Exception as e:
            current_app.logger.error(f"Error exporting analytics data: {str(e)}")
            return False, f"Export failed: {str(e)}", None

    @staticmethod
    def _convert_to_csv(data: Dict) -> str:
        """
        Convert analytics data to CSV format

        Args:
            data: Analytics data dictionary

        Returns:
            CSV formatted string
        """
        try:
            csv_lines = []

            # Header
            csv_lines.append("Product Evaluation System - Analytics Report")
            csv_lines.append(f"Generated: {data['export_info']['generated_at']}")
            csv_lines.append(
                f"Period: {data['export_info']['start_date']} to {data['export_info']['end_date']}"
            )
            csv_lines.append("")

            # Key Statistics
            csv_lines.append("Key Statistics")
            csv_lines.append("Metric,Value")
            stats = data["statistics"]
            for key, value in stats.items():
                if isinstance(value, dict):
                    continue  # Skip complex objects for CSV
                csv_lines.append(f"{key.replace('_', ' ').title()},{value}")
            csv_lines.append("")

            # User Performance
            csv_lines.append("User Performance")
            csv_lines.append(
                "Username,Role,Total Assigned,Completed,Completion Rate,Avg Days"
            )
            for user in data["user_performance"]:
                csv_lines.append(
                    f"{user['username']},{user['role']},{user['total_assigned']},"
                    f"{user['completed_assigned']},{user['completion_rate']},"
                    f"{user['average_completion_days']}"
                )

            return "\n".join(csv_lines)

        except Exception as e:
            current_app.logger.error(f"Error converting to CSV: {str(e)}")
            return "Error generating CSV data"

    @staticmethod
    def get_predictive_insights() -> Dict:
        """
        Generate predictive insights based on historical data

        Returns:
            Dictionary with predictive insights
        """
        try:
            insights = {}

            # Predict completion time based on evaluation type and current workload
            type_predictions = {}

            for eval_type in EvaluationType:
                # Get historical completion times for this type
                completed_evals = Evaluation.query.filter(
                    and_(
                        Evaluation.evaluation_type == eval_type,
                        Evaluation.status == EvaluationStatus.COMPLETED,
                        Evaluation.completed_at.isnot(None),
                    )
                ).all()

                if len(completed_evals) >= 3:  # Need minimum data for prediction
                    completion_times = [
                        (eval.completed_at - eval.created_at).days
                        for eval in completed_evals
                    ]

                    avg_time = sum(completion_times) / len(completion_times)

                    # Simple prediction: adjust based on current workload
                    current_workload = Evaluation.query.filter(
                        and_(
                            Evaluation.evaluation_type == eval_type,
                            Evaluation.status.in_(
                                [EvaluationStatus.PENDING, EvaluationStatus.IN_PROGRESS]
                            ),
                        )
                    ).count()

                    # Adjust prediction based on workload (simple linear adjustment)
                    workload_factor = 1 + (
                        current_workload * 0.1
                    )  # 10% increase per pending evaluation
                    predicted_time = round(avg_time * workload_factor, 1)

                    type_predictions[eval_type.value.lower().replace(" ", "_")] = {
                        "historical_average_days": round(avg_time, 1),
                        "current_workload": current_workload,
                        "predicted_completion_days": predicted_time,
                        "confidence": "medium" if len(completed_evals) >= 10 else "low",
                    }

            insights["completion_predictions"] = type_predictions

            # Identify potential bottlenecks
            potential_bottlenecks = []

            # Check for increasing trend in pending evaluations
            recent_pending = Evaluation.query.filter(
                and_(
                    Evaluation.status == EvaluationStatus.PENDING,
                    Evaluation.created_at >= datetime.utcnow() - timedelta(days=7),
                )
            ).count()

            older_pending = Evaluation.query.filter(
                and_(
                    Evaluation.status == EvaluationStatus.PENDING,
                    Evaluation.created_at >= datetime.utcnow() - timedelta(days=14),
                    Evaluation.created_at < datetime.utcnow() - timedelta(days=7),
                )
            ).count()

            if recent_pending > older_pending * 1.5:  # 50% increase
                potential_bottlenecks.append(
                    {
                        "type": "increasing_pending",
                        "description": "Pending evaluations are increasing rapidly",
                        "severity": "high",
                        "recommendation": "Consider reassigning workload or adding more reviewers",
                    }
                )

            insights["potential_bottlenecks"] = potential_bottlenecks

            return insights

        except Exception as e:
            current_app.logger.error(f"Error generating predictive insights: {str(e)}")
            return {}

"""Notifications API endpoints for Product Evaluation System

This module handles notification-related API endpoints including message management,
notification preferences, and in-app messaging.
"""

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from app.models.message import MessageStatus, MessageType
from app.services.notification_service import NotificationService
from app.utils.decorators import role_required, validate_json
from app.utils.helpers import get_current_user_id

# Create blueprint
notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/", methods=["GET"])
@jwt_required()
def get_user_notifications():
    """Get notifications for the current user

    Query parameters:
    - limit: int (default: 50)
    - status: str (optional filter by status)
    """
    try:
        current_user_id = get_current_user_id()

        # Get query parameters
        limit = request.args.get("limit", 50, type=int)
        status_filter = request.args.get("status")

        # Validate status filter if provided
        status_enum = None
        if status_filter:
            try:
                status_enum = MessageStatus(status_filter)
            except ValueError:
                return jsonify(
                    {
                        "error": f"Invalid status: {status_filter}",
                        "valid_statuses": [status.value for status in MessageStatus],
                    }
                ), 400

        # Get notifications
        notifications = NotificationService.get_user_notifications(
            user_id=current_user_id, limit=limit, status_filter=status_enum
        )

        # Get unread count
        unread_count = NotificationService.get_unread_count(current_user_id)

        return jsonify(
            {
                "notifications": notifications,
                "unread_count": unread_count,
                "total_returned": len(notifications),
            }
        ), 200

    except Exception as e:
        current_app.logger.error(f"Error getting user notifications: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@notifications_bp.route("/unread-count", methods=["GET"])
@jwt_required()
def get_unread_count():
    """Get count of unread notifications for the current user"""
    try:
        current_user_id = get_current_user_id()

        unread_count = NotificationService.get_unread_count(current_user_id)

        return jsonify({"unread_count": unread_count}), 200

    except Exception as e:
        current_app.logger.error(f"Error getting unread count: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@notifications_bp.route("/<int:message_id>/read", methods=["PUT"])
@jwt_required()
def mark_notification_as_read(message_id):
    """Mark a specific notification as read"""
    try:
        current_user_id = get_current_user_id()

        success = NotificationService.mark_as_read(message_id, current_user_id)

        if success:
            return jsonify(
                {"message": "Notification marked as read", "message_id": message_id}
            ), 200
        else:
            return jsonify({"error": "Notification not found or access denied"}), 404

    except Exception as e:
        current_app.logger.error(f"Error marking notification as read: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@notifications_bp.route("/mark-all-read", methods=["PUT"])
@jwt_required()
def mark_all_notifications_as_read():
    """Mark all notifications as read for the current user"""
    try:
        current_user_id = get_current_user_id()

        count = NotificationService.mark_all_as_read(current_user_id)

        return jsonify(
            {"message": f"Marked {count} notifications as read", "marked_count": count}
        ), 200

    except Exception as e:
        current_app.logger.error(f"Error marking all notifications as read: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@notifications_bp.route("/<int:message_id>", methods=["DELETE"])
@jwt_required()
def delete_notification(message_id):
    """Delete a specific notification"""
    try:
        current_user_id = get_current_user_id()

        success = NotificationService.delete_notification(message_id, current_user_id)

        if success:
            return jsonify(
                {
                    "message": "Notification deleted successfully",
                    "message_id": message_id,
                }
            ), 200
        else:
            return jsonify({"error": "Notification not found or access denied"}), 404

    except Exception as e:
        current_app.logger.error(f"Error deleting notification: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@notifications_bp.route("/send", methods=["POST"])
@jwt_required()
@validate_json(["recipient_id", "title", "content"])
def send_notification():
    """Send a notification to another user

    Required JSON fields:
    - recipient_id: int
    - title: str
    - content: str
    - message_type: str (optional, default: 'USER')
    - related_evaluation_id: int (optional)
    """
    try:
        data = request.get_json()
        current_user_id = get_current_user_id()

        recipient_id = data["recipient_id"]
        title = data["title"]
        content = data["content"]
        message_type_str = data.get("message_type", "USER")
        related_evaluation_id = data.get("related_evaluation_id")

        # Validate message type
        try:
            message_type = MessageType(message_type_str)
        except ValueError:
            return jsonify(
                {
                    "error": f"Invalid message type: {message_type_str}",
                    "valid_types": [msg_type.value for msg_type in MessageType],
                }
            ), 400

        # Send notification
        success = NotificationService.send_notification(
            sender_id=current_user_id,
            recipient_id=recipient_id,
            title=title,
            content=content,
            message_type=message_type,
            related_evaluation_id=related_evaluation_id,
        )

        if success:
            return jsonify(
                {
                    "message": "Notification sent successfully",
                    "recipient_id": recipient_id,
                }
            ), 201
        else:
            return jsonify({"error": "Failed to send notification"}), 400

    except Exception as e:
        current_app.logger.error(f"Error sending notification: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@notifications_bp.route("/send-bulk", methods=["POST"])
@jwt_required()
@role_required(["Admin", "Group Leader", "Part Leader"])
@validate_json(["recipient_ids", "title", "content"])
def send_bulk_notification():
    """Send a notification to multiple users (Leaders and Admin only)

    Required JSON fields:
    - recipient_ids: List[int]
    - title: str
    - content: str
    - message_type: str (optional, default: 'SYSTEM')
    - related_evaluation_id: int (optional)
    """
    try:
        data = request.get_json()
        current_user_id = get_current_user_id()

        recipient_ids = data["recipient_ids"]
        title = data["title"]
        content = data["content"]
        message_type_str = data.get("message_type", "SYSTEM")
        related_evaluation_id = data.get("related_evaluation_id")

        # Validate inputs
        if not isinstance(recipient_ids, list) or not recipient_ids:
            return jsonify({"error": "recipient_ids must be a non-empty list"}), 400

        try:
            message_type = MessageType(message_type_str)
        except ValueError:
            return jsonify(
                {
                    "error": f"Invalid message type: {message_type_str}",
                    "valid_types": [msg_type.value for msg_type in MessageType],
                }
            ), 400

        # Send bulk notification
        sent_count = NotificationService.send_bulk_notification(
            sender_id=current_user_id,
            recipient_ids=recipient_ids,
            title=title,
            content=content,
            message_type=message_type,
            related_evaluation_id=related_evaluation_id,
        )

        return jsonify(
            {
                "message": f"Bulk notification sent to {sent_count} users",
                "sent_count": sent_count,
                "total_recipients": len(recipient_ids),
            }
        ), 201

    except Exception as e:
        current_app.logger.error(f"Error sending bulk notification: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@notifications_bp.route("/statistics", methods=["GET"])
@jwt_required()
@role_required(["Admin"])
def get_notification_statistics():
    """Get notification system statistics (Admin only)"""
    try:
        stats = NotificationService.get_notification_statistics()

        return jsonify({"statistics": stats}), 200

    except Exception as e:
        current_app.logger.error(f"Error getting notification statistics: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@notifications_bp.route("/cleanup", methods=["POST"])
@jwt_required()
@role_required(["Admin"])
def cleanup_old_notifications():
    """Clean up old notifications (Admin only)

    Optional JSON fields:
    - days_to_keep: int (default: 90)
    """
    try:
        data = request.get_json() or {}
        days_to_keep = data.get("days_to_keep", 90)

        # Validate days_to_keep
        if not isinstance(days_to_keep, int) or days_to_keep < 1:
            return jsonify({"error": "days_to_keep must be a positive integer"}), 400

        # Perform cleanup
        NotificationService.cleanup_old_notifications(days_to_keep)

        return jsonify(
            {
                "message": f"Cleanup completed for notifications older than {days_to_keep} days"
            }
        ), 200

    except Exception as e:
        current_app.logger.error(f"Error cleaning up notifications: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@notifications_bp.route("/send-reminders", methods=["POST"])
@jwt_required()
@role_required(["Admin", "Group Leader"])
def send_reminder_notifications():
    """Send reminder notifications for overdue evaluations
    (Admin and Group Leader only)
    """
    try:
        # Send reminder notifications
        NotificationService.send_reminder_notifications()

        return jsonify({"message": "Reminder notifications sent successfully"}), 200

    except Exception as e:
        current_app.logger.error(f"Error sending reminder notifications: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@notifications_bp.route("/digest/<int:user_id>", methods=["POST"])
@jwt_required()
@role_required(["Admin"])
def send_daily_digest(user_id):
    """Send daily digest to a specific user (Admin only)"""
    try:
        success = NotificationService.send_daily_digest(user_id)

        if success:
            return jsonify({"message": f"Daily digest sent to user {user_id}"}), 200
        else:
            return jsonify(
                {"error": "Failed to send daily digest or user not found"}
            ), 400

    except Exception as e:
        current_app.logger.error(f"Error sending daily digest: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

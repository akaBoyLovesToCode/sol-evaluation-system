"""Notification Service for Product Evaluation System

This service handles in-app notification system as specified in Phase 2 requirements.
Manages message creation, delivery, and notification preferences.
"""

from datetime import datetime, timedelta

from flask import current_app
from sqlalchemy import and_, desc, or_

from app import db
from app.models.evaluation import Evaluation
from app.models.message import Message, MessageStatus, MessageType
from app.models.user import User, UserRole


class NotificationService:
    """Service class for managing in-app notifications and messages

    Handles:
    - Message creation and delivery
    - Notification preferences
    - Bulk notifications
    - Message status management
    """

    @staticmethod
    def send_notification(
        sender_id: int,
        recipient_id: int,
        title: str,
        content: str,
        message_type: MessageType = MessageType.SYSTEM,
        related_evaluation_id: int | None = None,
    ) -> bool:
        """Send a notification to a specific user

        Args:
            sender_id: ID of the sender (can be system user)
            recipient_id: ID of the recipient
            title: Notification title
            content: Notification content
            message_type: Type of message
            related_evaluation_id: Optional related evaluation ID

        Returns:
            bool: Success status

        """
        try:
            # Validate users exist
            sender = User.query.get(sender_id)
            recipient = User.query.get(recipient_id)

            if not sender or not recipient:
                current_app.logger.error(
                    f"Invalid sender ({sender_id}) or recipient ({recipient_id})"
                )
                return False

            # Create message
            message = Message(
                sender_id=sender_id,
                recipient_id=recipient_id,
                message_type=message_type,
                title=title,
                content=content,
                related_evaluation_id=related_evaluation_id,
                status=MessageStatus.UNREAD,
            )

            db.session.add(message)
            db.session.commit()

            current_app.logger.info(
                f"Notification sent from {sender.username} to {recipient.username}"
            )
            return True

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error sending notification: {str(e)}")
            return False

    @staticmethod
    def send_bulk_notification(
        sender_id: int,
        recipient_ids: list[int],
        title: str,
        content: str,
        message_type: MessageType = MessageType.SYSTEM,
        related_evaluation_id: int | None = None,
    ) -> int:
        """Send notifications to multiple users

        Args:
            sender_id: ID of the sender
            recipient_ids: List of recipient IDs
            title: Notification title
            content: Notification content
            message_type: Type of message
            related_evaluation_id: Optional related evaluation ID

        Returns:
            int: Number of notifications sent successfully

        """
        try:
            sent_count = 0

            # Validate sender exists
            sender = User.query.get(sender_id)
            if not sender:
                return 0

            # Get valid recipients
            valid_recipients = User.query.filter(
                and_(User.id.in_(recipient_ids), User.is_active)
            ).all()

            # Create messages for all valid recipients
            for recipient in valid_recipients:
                message = Message(
                    sender_id=sender_id,
                    recipient_id=recipient.id,
                    message_type=message_type,
                    title=title,
                    content=content,
                    related_evaluation_id=related_evaluation_id,
                    status=MessageStatus.UNREAD,
                )
                db.session.add(message)
                sent_count += 1

            db.session.commit()
            current_app.logger.info(f"Bulk notification sent to {sent_count} users")
            return sent_count

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error sending bulk notification: {str(e)}")
            return 0

    @staticmethod
    def get_user_notifications(
        user_id: int, limit: int = 50, status_filter: MessageStatus | None = None
    ) -> list[dict]:
        """Get notifications for a specific user

        Args:
            user_id: ID of the user
            limit: Maximum number of notifications to return
            status_filter: Optional status filter

        Returns:
            List of notification dictionaries

        """
        try:
            query = Message.query.filter_by(recipient_id=user_id)

            if status_filter:
                query = query.filter_by(status=status_filter)

            messages = query.order_by(desc(Message.created_at)).limit(limit).all()

            result = []
            for message in messages:
                result.append(
                    {
                        "id": message.id,
                        "title": message.title,
                        "content": message.content,
                        "message_type": message.message_type.value,
                        "status": message.status.value,
                        "created_at": message.created_at.isoformat(),
                        "read_at": message.read_at.isoformat()
                        if message.read_at
                        else None,
                        "sender": message.sender.username
                        if message.sender
                        else "System",
                        "related_evaluation_id": message.related_evaluation_id,
                        "related_evaluation_title": message.related_evaluation.title
                        if message.related_evaluation
                        else None,
                    }
                )

            return result

        except Exception as e:
            current_app.logger.error(f"Error getting user notifications: {str(e)}")
            return []

    @staticmethod
    def mark_as_read(message_id: int, user_id: int) -> bool:
        """Mark a notification as read

        Args:
            message_id: ID of the message
            user_id: ID of the user (for security check)

        Returns:
            bool: Success status

        """
        try:
            message = Message.query.filter_by(
                id=message_id, recipient_id=user_id
            ).first()

            if not message:
                return False

            if message.status == MessageStatus.UNREAD:
                message.status = MessageStatus.READ
                message.read_at = datetime.utcnow()
                db.session.commit()

            return True

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error marking message as read: {str(e)}")
            return False

    @staticmethod
    def mark_all_as_read(user_id: int) -> int:
        """Mark all notifications as read for a user

        Args:
            user_id: ID of the user

        Returns:
            int: Number of messages marked as read

        """
        try:
            unread_messages = Message.query.filter_by(
                recipient_id=user_id, status=MessageStatus.UNREAD
            ).all()

            count = 0
            for message in unread_messages:
                message.status = MessageStatus.READ
                message.read_at = datetime.utcnow()
                count += 1

            db.session.commit()
            return count

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error marking all messages as read: {str(e)}")
            return 0

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """Get count of unread notifications for a user

        Args:
            user_id: ID of the user

        Returns:
            int: Number of unread notifications

        """
        try:
            count = Message.query.filter_by(
                recipient_id=user_id, status=MessageStatus.UNREAD
            ).count()

            return count

        except Exception as e:
            current_app.logger.error(f"Error getting unread count: {str(e)}")
            return 0

    @staticmethod
    def delete_notification(message_id: int, user_id: int) -> bool:
        """Delete a notification (soft delete by marking as deleted)

        Args:
            message_id: ID of the message
            user_id: ID of the user (for security check)

        Returns:
            bool: Success status

        """
        try:
            message = Message.query.filter_by(
                id=message_id, recipient_id=user_id
            ).first()

            if not message:
                return False

            message.status = MessageStatus.DELETED
            db.session.commit()

            return True

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting notification: {str(e)}")
            return False

    @staticmethod
    def send_reminder_notifications():
        """Send reminder notifications for overdue evaluations
        This method can be called by a scheduled task
        """
        try:
            # Find overdue evaluations
            overdue_evaluations = Evaluation.query.filter(
                and_(
                    Evaluation.due_date < datetime.utcnow().date(),
                    Evaluation.status.in_(["PENDING", "IN_PROGRESS"]),
                )
            ).all()

            sent_count = 0

            for evaluation in overdue_evaluations:
                # Check if reminder was already sent today
                today = datetime.utcnow().date()
                existing_reminder = Message.query.filter(
                    and_(
                        Message.related_evaluation_id == evaluation.id,
                        Message.title.like("%Overdue%"),
                        Message.created_at >= today,
                    )
                ).first()

                if existing_reminder:
                    continue  # Skip if reminder already sent today

                # Determine who to notify
                recipients = []
                if evaluation.assigned_to:
                    recipients.append(evaluation.assigned_to)
                if evaluation.part_leader_id:
                    recipients.append(evaluation.part_leader_id)
                if evaluation.group_leader_id:
                    recipients.append(evaluation.group_leader_id)

                # Remove duplicates
                recipients = list(set(recipients))

                # Send reminders
                days_overdue = (datetime.utcnow().date() - evaluation.due_date).days
                title = f"Overdue Evaluation: {evaluation.title}"
                content = f"Evaluation '{evaluation.title}' is {days_overdue} days overdue. Please take action."

                for recipient_id in recipients:
                    NotificationService.send_notification(
                        sender_id=1,  # System user
                        recipient_id=recipient_id,
                        title=title,
                        content=content,
                        message_type=MessageType.REMINDER,
                        related_evaluation_id=evaluation.id,
                    )
                    sent_count += 1

            current_app.logger.info(f"Sent {sent_count} overdue reminder notifications")

        except Exception as e:
            current_app.logger.error(f"Error sending reminder notifications: {str(e)}")

    @staticmethod
    def send_daily_digest(user_id: int) -> bool:
        """Send daily digest of activities to a user

        Args:
            user_id: ID of the user

        Returns:
            bool: Success status

        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False

            # Get yesterday's date for digest
            yesterday = datetime.utcnow().date() - timedelta(days=1)

            # Collect digest information
            digest_items = []

            # New evaluations assigned to user
            new_assignments = Evaluation.query.filter(
                and_(
                    Evaluation.assigned_to == user_id,
                    Evaluation.created_at >= yesterday,
                )
            ).count()

            if new_assignments > 0:
                digest_items.append(
                    f"• {new_assignments} new evaluation(s) assigned to you"
                )

            # Evaluations requiring approval (for leaders)
            if user.role in [UserRole.PART_LEADER, UserRole.GROUP_LEADER]:
                pending_approvals = 0
                if user.role == UserRole.PART_LEADER:
                    pending_approvals = Evaluation.query.filter(
                        and_(
                            Evaluation.part_leader_id == user_id,
                            Evaluation.status == "PENDING",
                        )
                    ).count()
                elif user.role == UserRole.GROUP_LEADER:
                    pending_approvals = Evaluation.query.filter(
                        and_(
                            Evaluation.group_leader_id == user_id,
                            Evaluation.status == "IN_PROGRESS",
                        )
                    ).count()

                if pending_approvals > 0:
                    digest_items.append(
                        f"• {pending_approvals} evaluation(s) pending your approval"
                    )

            # Overdue evaluations
            overdue_count = Evaluation.query.filter(
                and_(
                    or_(
                        Evaluation.assigned_to == user_id,
                        Evaluation.created_by == user_id,
                    ),
                    Evaluation.due_date < datetime.utcnow().date(),
                    Evaluation.status != "COMPLETED",
                )
            ).count()

            if overdue_count > 0:
                digest_items.append(f"• {overdue_count} overdue evaluation(s)")

            # Only send digest if there are items to report
            if digest_items:
                content = "Daily Digest:\n\n" + "\n".join(digest_items)

                return NotificationService.send_notification(
                    sender_id=1,  # System user
                    recipient_id=user_id,
                    title="Daily Evaluation Digest",
                    content=content,
                    message_type=MessageType.DIGEST,
                )

            return True

        except Exception as e:
            current_app.logger.error(f"Error sending daily digest: {str(e)}")
            return False

    @staticmethod
    def cleanup_old_notifications(days_to_keep: int = 90):
        """Clean up old notifications to prevent database bloat

        Args:
            days_to_keep: Number of days to keep notifications

        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

            # Delete old read and deleted messages
            old_messages = Message.query.filter(
                and_(
                    Message.created_at < cutoff_date,
                    Message.status.in_([MessageStatus.READ, MessageStatus.DELETED]),
                )
            ).all()

            count = len(old_messages)
            for message in old_messages:
                db.session.delete(message)

            db.session.commit()
            current_app.logger.info(f"Cleaned up {count} old notifications")

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error cleaning up old notifications: {str(e)}")

    @staticmethod
    def get_notification_statistics() -> dict:
        """Get notification statistics for admin dashboard

        Returns:
            Dictionary with notification statistics

        """
        try:
            stats = {}

            # Total messages by type
            for msg_type in MessageType:
                count = Message.query.filter_by(message_type=msg_type).count()
                stats[f"{msg_type.value.lower()}_messages"] = count

            # Messages by status
            for status in MessageStatus:
                count = Message.query.filter_by(status=status).count()
                stats[f"{status.value.lower()}_messages"] = count

            # Messages sent in last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_count = Message.query.filter(Message.created_at >= yesterday).count()
            stats["recent_messages"] = recent_count

            # Average response time (time between message sent and read)
            read_messages = Message.query.filter(
                and_(Message.status == MessageStatus.READ, Message.read_at.isnot(None))
            ).all()

            if read_messages:
                total_response_time = sum(
                    [
                        (msg.read_at - msg.created_at).total_seconds()
                        / 3600  # Convert to hours
                        for msg in read_messages
                    ]
                )
                stats["average_response_hours"] = round(
                    total_response_time / len(read_messages), 1
                )
            else:
                stats["average_response_hours"] = 0

            return stats

        except Exception as e:
            current_app.logger.error(f"Error getting notification statistics: {str(e)}")
            return {}

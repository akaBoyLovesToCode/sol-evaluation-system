from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from app import db
from app.models import User, Message
from app.utils.decorators import require_role, validate_json, handle_exceptions
from app.utils.validators import validate_email, validate_password, validate_username
from app.utils.helpers import (
    calculate_pagination,
    build_query_filters,
    create_response,
    get_current_user_id,
)

# Create user blueprint
user_bp = Blueprint("user", __name__)


@user_bp.route("", methods=["GET"])
@jwt_required()
@require_role("part_leader")
@handle_exceptions
def get_users():
    """
    Get list of users with filtering and pagination

    Query parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    - role: Filter by role
    - is_active: Filter by active status
    - department: Filter by department
    - search: Search in username, email, or full name
    """
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        # Build base query
        query = User.query

        # Apply filters
        filters = {}

        if request.args.get("role"):
            filters["role"] = request.args.get("role")

        if request.args.get("is_active") is not None:
            filters["is_active"] = request.args.get("is_active").lower() == "true"

        if request.args.get("department"):
            filters["department"] = {"like": request.args.get("department")}

        # Search functionality
        search_term = request.args.get("search")
        if search_term:
            search_filter = (
                User.username.like(f"%{search_term}%")
                | User.email.like(f"%{search_term}%")
                | User.full_name.like(f"%{search_term}%")
            )
            query = query.filter(search_filter)

        # Apply other filters
        filter_conditions = build_query_filters(User, filters)
        for condition in filter_conditions:
            query = query.filter(condition)

        # Order by creation date (newest first)
        query = query.order_by(User.created_at.desc())

        # Get total count for pagination
        total_count = query.count()

        # Apply pagination
        pagination_info = calculate_pagination(page, per_page, total_count)
        users = query.offset(pagination_info["offset"]).limit(per_page).all()

        # Convert to dictionaries (exclude sensitive data)
        user_list = [user.to_dict() for user in users]

        return create_response(
            data={"users": user_list, "pagination": pagination_info},
            message="Users retrieved successfully",
        )

    except Exception as e:
        current_app.logger.error(f"Get users error: {str(e)}")
        return create_response(message="Failed to retrieve users", status_code=500)


@user_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
@handle_exceptions
def get_user(user_id):
    """Get single user by ID"""
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)

        # Users can view their own profile, leaders can view others
        if user_id != current_user_id and not current_user.has_permission(
            "part_leader"
        ):
            return create_response(message="Permission denied", status_code=403)

        user = User.query.get(user_id)
        if not user:
            return create_response(message="User not found", status_code=404)

        return create_response(
            data={"user": user.to_dict()}, message="User retrieved successfully"
        )

    except Exception as e:
        current_app.logger.error(f"Get user error: {str(e)}")
        return create_response(message="Failed to retrieve user", status_code=500)


@user_bp.route("", methods=["POST"])
@jwt_required()
@require_role("admin")
@validate_json(required_fields=["username", "email", "password", "full_name"])
@handle_exceptions
def create_user():
    """Create new user (admin only)"""
    try:
        data = request.get_json()

        # Validate input data
        username = data["username"].strip()
        email = data["email"].strip()
        password = data["password"]
        full_name = data["full_name"].strip()
        role = data.get("role", "user")

        # Validate username
        username_validation = validate_username(username)
        if not username_validation["valid"]:
            return create_response(
                message=username_validation["message"], status_code=400
            )

        # Validate email
        email_validation = validate_email(email)
        if not email_validation["valid"]:
            return create_response(message=email_validation["message"], status_code=400)

        # Validate password
        password_validation = validate_password(password)
        if not password_validation["valid"]:
            return create_response(
                message=password_validation["message"], status_code=400
            )

        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            if existing_user.username == username:
                return create_response(
                    message="Username already exists", status_code=409
                )
            else:
                return create_response(message="Email already exists", status_code=409)

        # Create new user
        user = User(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role=role,
            department=data.get("department"),
            phone=data.get("phone"),
        )

        db.session.add(user)
        db.session.commit()

        return create_response(
            data={"user": user.to_dict()},
            message="User created successfully",
            status_code=201,
        )

    except Exception as e:
        current_app.logger.error(f"Create user error: {str(e)}")
        db.session.rollback()
        return create_response(message="Failed to create user", status_code=500)


@user_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
@validate_json()
@handle_exceptions
def update_user(user_id):
    """Update user information"""
    try:
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)
        data = request.get_json()

        user = User.query.get(user_id)
        if not user:
            return create_response(message="User not found", status_code=404)

        # Check permissions
        can_edit = (
            user_id == current_user_id  # Users can edit themselves
            or current_user.has_permission("admin")  # Admins can edit anyone
        )

        if not can_edit:
            return create_response(message="Permission denied", status_code=403)

        # Fields that users can update themselves
        user_editable_fields = ["full_name", "department", "phone"]

        # Fields that only admins can update
        admin_only_fields = ["username", "email", "role", "is_active"]

        # Update user-editable fields
        for field in user_editable_fields:
            if field in data:
                setattr(user, field, data[field])

        # Update admin-only fields (if user is admin)
        if current_user.has_permission("admin"):
            for field in admin_only_fields:
                if field in data:
                    # Special validation for certain fields
                    if field == "username":
                        username_validation = validate_username(data[field])
                        if not username_validation["valid"]:
                            return create_response(
                                message=username_validation["message"], status_code=400
                            )

                        # Check if username already exists (excluding current user)
                        existing_user = User.query.filter(
                            User.username == data[field], User.id != user_id
                        ).first()
                        if existing_user:
                            return create_response(
                                message="Username already exists", status_code=409
                            )

                    elif field == "email":
                        email_validation = validate_email(data[field])
                        if not email_validation["valid"]:
                            return create_response(
                                message=email_validation["message"], status_code=400
                            )

                        # Check if email already exists (excluding current user)
                        existing_user = User.query.filter(
                            User.email == data[field], User.id != user_id
                        ).first()
                        if existing_user:
                            return create_response(
                                message="Email already exists", status_code=409
                            )

                    setattr(user, field, data[field])

        db.session.commit()

        return create_response(
            data={"user": user.to_dict()}, message="User updated successfully"
        )

    except Exception as e:
        current_app.logger.error(f"Update user error: {str(e)}")
        db.session.rollback()
        return create_response(message="Failed to update user", status_code=500)


@user_bp.route("/<int:user_id>/deactivate", methods=["POST"])
@jwt_required()
@require_role("admin")
@handle_exceptions
def deactivate_user(user_id):
    """Deactivate user account"""
    try:
        current_user_id = get_current_user_id()

        # Cannot deactivate yourself
        if user_id == current_user_id:
            return create_response(
                message="Cannot deactivate your own account", status_code=400
            )

        user = User.query.get(user_id)
        if not user:
            return create_response(message="User not found", status_code=404)

        if not user.is_active:
            return create_response(message="User is already inactive", status_code=400)

        user.is_active = False
        db.session.commit()

        return create_response(
            data={"user": user.to_dict()}, message="User deactivated successfully"
        )

    except Exception as e:
        current_app.logger.error(f"Deactivate user error: {str(e)}")
        db.session.rollback()
        return create_response(message="Failed to deactivate user", status_code=500)


@user_bp.route("/<int:user_id>/activate", methods=["POST"])
@jwt_required()
@require_role("admin")
@handle_exceptions
def activate_user(user_id):
    """Activate user account"""
    try:
        user = User.query.get(user_id)
        if not user:
            return create_response(message="User not found", status_code=404)

        if user.is_active:
            return create_response(message="User is already active", status_code=400)

        user.is_active = True
        db.session.commit()

        return create_response(
            data={"user": user.to_dict()}, message="User activated successfully"
        )

    except Exception as e:
        current_app.logger.error(f"Activate user error: {str(e)}")
        db.session.rollback()
        return create_response(message="Failed to activate user", status_code=500)


@user_bp.route("/<int:user_id>/reset-password", methods=["POST"])
@jwt_required()
@require_role("admin")
@validate_json(required_fields=["new_password"])
@handle_exceptions
def reset_user_password(user_id):
    """Reset user password (admin only)"""
    try:
        data = request.get_json()
        new_password = data["new_password"]

        # Validate new password
        password_validation = validate_password(new_password)
        if not password_validation["valid"]:
            return create_response(
                message=password_validation["message"], status_code=400
            )

        user = User.query.get(user_id)
        if not user:
            return create_response(message="User not found", status_code=404)

        # Update password
        user.set_password(new_password)
        db.session.commit()

        return create_response(message="Password reset successfully")

    except Exception as e:
        current_app.logger.error(f"Reset password error: {str(e)}")
        db.session.rollback()
        return create_response(message="Failed to reset password", status_code=500)


@user_bp.route("/messages", methods=["GET"])
@jwt_required()
@handle_exceptions
def get_user_messages():
    """Get current user's messages"""
    try:
        current_user_id = get_current_user_id()

        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        unread_only = request.args.get("unread_only", "false").lower() == "true"

        # Build query
        query = Message.query.filter_by(recipient_id=current_user_id)

        if unread_only:
            query = query.filter_by(is_read=False)

        # Order by creation date (newest first)
        query = query.order_by(Message.created_at.desc())

        # Get total count for pagination
        total_count = query.count()

        # Apply pagination
        pagination_info = calculate_pagination(page, per_page, total_count)
        messages = query.offset(pagination_info["offset"]).limit(per_page).all()

        # Convert to dictionaries
        message_list = [message.to_dict() for message in messages]

        return create_response(
            data={
                "messages": message_list,
                "pagination": pagination_info,
                "unread_count": Message.query.filter_by(
                    recipient_id=current_user_id, is_read=False
                ).count(),
            },
            message="Messages retrieved successfully",
        )

    except Exception as e:
        current_app.logger.error(f"Get messages error: {str(e)}")
        return create_response(message="Failed to retrieve messages", status_code=500)


@user_bp.route("/messages/<int:message_id>/read", methods=["POST"])
@jwt_required()
@handle_exceptions
def mark_message_read(message_id):
    """Mark message as read"""
    try:
        current_user_id = get_current_user_id()

        message = Message.query.filter_by(
            id=message_id, recipient_id=current_user_id
        ).first()

        if not message:
            return create_response(message="Message not found", status_code=404)

        message.mark_as_read()

        return create_response(message="Message marked as read")

    except Exception as e:
        current_app.logger.error(f"Mark message read error: {str(e)}")
        return create_response(
            message="Failed to mark message as read", status_code=500
        )


@user_bp.route("/messages/mark-all-read", methods=["POST"])
@jwt_required()
@handle_exceptions
def mark_all_messages_read():
    """Mark all messages as read for current user"""
    try:
        current_user_id = get_current_user_id()

        # Update all unread messages for the user
        Message.query.filter_by(recipient_id=current_user_id, is_read=False).update(
            {"is_read": True, "read_at": db.func.now()}
        )

        db.session.commit()

        return create_response(message="All messages marked as read")

    except Exception as e:
        current_app.logger.error(f"Mark all messages read error: {str(e)}")
        db.session.rollback()
        return create_response(
            message="Failed to mark all messages as read", status_code=500
        )

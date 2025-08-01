"""API endpoints for user management.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db
from app.models.user import User, UserRole
from app.models.operation_log import OperationLog, OperationType
from werkzeug.security import generate_password_hash
import json

user_bp = Blueprint("user", __name__)


@user_bp.route("", methods=["GET"])
@jwt_required()
def get_users():
    """Get a list of users with optional filtering.
    ---
    tags:
      - Users
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
      - name: username
        in: query
        schema:
          type: string
        description: Filter by username (partial match)
      - name: role
        in: query
        schema:
          type: string
          enum: [user, part_leader, group_leader, admin]
        description: Filter by user role
      - name: is_active
        in: query
        schema:
          type: boolean
        description: Filter by active status
    responses:
      200:
        description: List of users
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
                    users:
                      type: array
                      items:
                        type: object
                        properties:
                          id:
                            type: integer
                          username:
                            type: string
                          email:
                            type: string
                          fullName:
                            type: string
                          role:
                            type: string
                          department:
                            type: string
                          position:
                            type: string
                          is_active:
                            type: boolean
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
      403:
        description: Forbidden - User is not an admin
      500:
        description: Internal server error

    """
    try:
        # Check if user is admin
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role != UserRole.ADMIN.value:
            return jsonify(
                {"success": False, "message": "Unauthorized - Admin access required"}
            ), 403

        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        username = request.args.get("username")
        role = request.args.get("role")
        is_active = request.args.get("is_active")

        # Build query
        query = User.query

        # Apply filters
        if username:
            query = query.filter(User.username.ilike(f"%{username}%"))
        if role:
            query = query.filter(User.role == role)
        if is_active is not None:
            is_active_bool = is_active.lower() == "true"
            query = query.filter(User.is_active == is_active_bool)

        # Paginate results
        paginated_users = query.paginate(page=page, per_page=per_page, error_out=False)

        # Format response
        users_data = []
        for user in paginated_users.items:
            user_data = user.to_dict()
            users_data.append(user_data)

        # Log operation
        log = OperationLog(
            user_id=user_id,
            operation_type=OperationType.VIEW.value,
            target_type="user_list",
            target_id=None,
            target_description="Viewed user list",
            operation_description=f"Admin viewed user list with filters: {request.args}",
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
                    "users": users_data,
                    "total": paginated_users.total,
                    "page": page,
                    "per_page": per_page,
                    "pages": paginated_users.pages,
                },
            }
        )
    except Exception as e:
        current_app.logger.error(f"Error getting users: {str(e)}")
        return jsonify(
            {"success": False, "message": "Failed to get users", "error": str(e)}
        ), 500


@user_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    """Get details of a specific user.
    ---
    tags:
      - Users
    security:
      - bearerAuth: []

    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the user to retrieve
    responses:
      200:
        description: User details
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
                    user:
                      type: object
                      properties:
                        id:
                          type: integer
                        username:
                          type: string
                        email:
                          type: string
                        fullName:
                          type: string
                        role:
                          type: string
                        department:
                          type: string
                        position:
                          type: string
                        is_active:
                          type: boolean
      401:
        description: Unauthorized
      403:
        description: Forbidden - User is not an admin
      404:
        description: User not found
      500:
        description: Internal server error

    """
    try:
        # Check if user is admin or the requested user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user or (
            current_user.role != UserRole.ADMIN.value and current_user_id != user_id
        ):
            return jsonify(
                {
                    "success": False,
                    "message": "Unauthorized - Admin access or own profile required",
                }
            ), 403

        user = User.query.get(user_id)

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Log operation
        log = OperationLog(
            user_id=current_user_id,
            operation_type=OperationType.VIEW.value,
            target_type="user",
            target_id=user_id,
            target_description=f"Viewed user {user.username}",
            operation_description=f"User viewed user details",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            success=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({"success": True, "data": {"user": user.to_dict()}})
    except Exception as e:
        current_app.logger.error(f"Error getting user: {str(e)}")
        return jsonify(
            {"success": False, "message": "Failed to get user", "error": str(e)}
        ), 500


@user_bp.route("", methods=["POST"])
@jwt_required()
def create_user():
    """Create a new user.
    ---
    tags:
      - Users
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - username
              - email
              - fullName
              - password
              - role
            properties:
              username:
                type: string
                description: Username for login
              email:
                type: string
                format: email
                description: Email address
              fullName:
                type: string
                description: Full name of the user
              password:
                type: string
                format: password
                description: Password
              role:
                type: string
                enum: [user, part_leader, group_leader, admin]
                description: User role
              department:
                type: string
                description: Department
              position:
                type: string
                description: Position
              is_active:
                type: boolean
                description: Whether the user is active
                default: true
    responses:
      201:
        description: User created successfully
      400:
        description: Invalid request data
      401:
        description: Unauthorized
      403:
        description: Forbidden - User is not an admin
      500:
        description: Internal server error
    """
    try:
        # Check if user is admin
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user or current_user.role != UserRole.ADMIN.value:
            return jsonify(
                {"success": False, "message": "Unauthorized - Admin access required"}
            ), 403

        data = request.json

        # Validate required fields
        required_fields = ["username", "email", "fullName", "password", "role"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify(
                    {"success": False, "message": f"Missing required field: {field}"}
                ), 400

        # Check if username or email already exists
        if User.query.filter_by(username=data["username"]).first():
            return jsonify(
                {"success": False, "message": "Username already exists"}
            ), 400

        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"success": False, "message": "Email already exists"}), 400

        # Create user
        user = User(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            full_name=data["fullName"],
            role=data["role"],
            department=data.get("department", ""),
            position=data.get("position", ""),
            is_active=data.get("is_active", True),
        )

        db.session.add(user)
        db.session.commit()

        # Log operation
        log = OperationLog(
            user_id=current_user_id,
            operation_type=OperationType.CREATE.value,
            target_type="user",
            target_id=user.id,
            target_description=f"Created user {user.username}",
            operation_description="Admin created a new user",
            new_data=json.dumps({**user.to_dict(), "password": "[REDACTED]"}),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            success=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "User created successfully",
                "data": {"user": user.to_dict()},
            }
        ), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating user: {str(e)}")
        return jsonify(
            {"success": False, "message": "Failed to create user", "error": str(e)}
        ), 500


@user_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    """Update an existing user.
    ---
    tags:
      - Users
    security:
      - bearerAuth: []

    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the user to update
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
                format: email
                description: Email address
              fullName:
                type: string
                description: Full name of the user
              role:
                type: string
                enum: [user, part_leader, group_leader, admin]
                description: User role
              department:
                type: string
                description: Department
              position:
                type: string
                description: Position
              is_active:
                type: boolean
                description: Whether the user is active
    responses:
      200:
        description: User updated successfully
      400:
        description: Invalid request data
      401:
        description: Unauthorized
      403:
        description: Forbidden - User is not an admin
      404:
        description: User not found
      500:
        description: Internal server error

    """
    try:
        # Check if user is admin or the requested user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user:
            return jsonify({"success": False, "message": "Unauthorized"}), 401

        # Only admins can update role and active status
        data = request.json
        is_admin = current_user.role == UserRole.ADMIN.value
        is_self = current_user_id == user_id

        if not is_admin and not is_self:
            return jsonify(
                {
                    "success": False,
                    "message": "Unauthorized - Admin access or own profile required",
                }
            ), 403

        if not is_admin and ("role" in data or "is_active" in data):
            return jsonify(
                {
                    "success": False,
                    "message": "Unauthorized - Admin access required to update role or active status",
                }
            ), 403

        user = User.query.get(user_id)

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Store old data for logging
        old_data = user.to_dict()

        # Update fields
        if "email" in data and data["email"] != user.email:
            # Check if email already exists
            if User.query.filter_by(email=data["email"]).first():
                return jsonify(
                    {"success": False, "message": "Email already exists"}
                ), 400
            user.email = data["email"]

        if "fullName" in data:
            user.full_name = data["fullName"]

        if "department" in data:
            user.department = data["department"]

        if "position" in data:
            user.position = data["position"]

        if is_admin and "role" in data:
            user.role = data["role"]

        if is_admin and "is_active" in data:
            user.is_active = data["is_active"]

        db.session.commit()

        # Log operation
        log = OperationLog(
            user_id=current_user_id,
            operation_type=OperationType.UPDATE.value,
            target_type="user",
            target_id=user.id,
            target_description=f"Updated user {user.username}",
            operation_description="User profile updated",
            old_data=json.dumps(old_data),
            new_data=json.dumps(user.to_dict()),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            success=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "User updated successfully",
                "data": {"user": user.to_dict()},
            }
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating user: {str(e)}")
        return jsonify(
            {"success": False, "message": "Failed to update user", "error": str(e)}
        ), 500


@user_bp.route("/<int:user_id>/status", methods=["PUT"])
@jwt_required()
def update_user_status(user_id):
    """Update a user's active status.
    ---
    tags:
      - Users
    security:
      - bearerAuth: []

    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the user to update
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - is_active
            properties:
              is_active:
                type: boolean
                description: Whether the user is active
    responses:
      200:
        description: User status updated successfully
      400:
        description: Invalid request data
      401:
        description: Unauthorized
      403:
        description: Forbidden - User is not an admin
      404:
        description: User not found
      500:
        description: Internal server error

    """
    try:
        # Check if user is admin
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user or current_user.role != UserRole.ADMIN.value:
            return jsonify(
                {"success": False, "message": "Unauthorized - Admin access required"}
            ), 403

        data = request.json

        if "is_active" not in data:
            return jsonify(
                {"success": False, "message": "is_active field is required"}
            ), 400

        user = User.query.get(user_id)

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Store old data for logging
        old_data = {"is_active": user.is_active}

        # Update status
        user.is_active = data["is_active"]
        db.session.commit()

        # Log operation
        action = "activated" if user.is_active else "deactivated"
        log = OperationLog(
            user_id=current_user_id,
            operation_type=OperationType.UPDATE.value,
            target_type="user_status",
            target_id=user.id,
            target_description=f"{action.capitalize()} user {user.username}",
            operation_description=f"Admin {action} user account",
            old_data=json.dumps(old_data),
            new_data=json.dumps({"is_active": user.is_active}),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            success=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"User {action} successfully",
                "data": {"user": user.to_dict()},
            }
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating user status: {str(e)}")
        return jsonify(
            {
                "success": False,
                "message": "Failed to update user status",
                "error": str(e),
            }
        ), 500


@user_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    """Delete a user.
    ---
    tags:
      - Users
    security:
      - bearerAuth: []

    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
        description: ID of the user to delete
    responses:
      200:
        description: User deleted successfully
      401:
        description: Unauthorized
      403:
        description: Forbidden - User is not an admin
      404:
        description: User not found
      500:
        description: Internal server error

    """
    try:
        # Check if user is admin
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user or current_user.role != UserRole.ADMIN.value:
            return jsonify(
                {"success": False, "message": "Unauthorized - Admin access required"}
            ), 403

        user = User.query.get(user_id)

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Store user data for logging
        user_data = user.to_dict()

        # Delete user
        db.session.delete(user)
        db.session.commit()

        # Log operation
        log = OperationLog(
            user_id=current_user_id,
            operation_type=OperationType.DELETE.value,
            target_type="user",
            target_id=user_id,
            target_description=f"Deleted user {user_data['username']}",
            operation_description="Admin deleted user account",
            old_data=json.dumps(user_data),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            success=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({"success": True, "message": "User deleted successfully"})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting user: {str(e)}")
        return jsonify(
            {"success": False, "message": "Failed to delete user", "error": str(e)}
        ), 500


@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Get the current user's profile.
    ---
    tags:
      - Users
    security:
      - bearerAuth: []
    responses:
      200:
        description: User profile
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
                    user:
                      type: object
                      properties:
                        id:
                          type: integer
                        username:
                          type: string
                        email:
                          type: string
                        fullName:
                          type: string
                        role:
                          type: string
                        department:
                          type: string
                        position:
                          type: string
                        is_active:
                          type: boolean
      401:
        description: Unauthorized
      404:
        description: User not found
      500:
        description: Internal server error
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        return jsonify({"success": True, "data": {"user": user.to_dict()}})
    except Exception as e:
        current_app.logger.error(f"Error getting user profile: {str(e)}")
        return jsonify(
            {"success": False, "message": "Failed to get user profile", "error": str(e)}
        ), 500


@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update the current user's profile.
    ---
    tags:
      - Users
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
                format: email
                description: Email address
              fullName:
                type: string
                description: Full name of the user
              department:
                type: string
                description: Department
              position:
                type: string
                description: Position
    responses:
      200:
        description: Profile updated successfully
      400:
        description: Invalid request data
      401:
        description: Unauthorized
      404:
        description: User not found
      500:
        description: Internal server error
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        data = request.json

        # Store old data for logging
        old_data = user.to_dict()

        # Update fields
        if "email" in data and data["email"] != user.email:
            # Check if email already exists
            if User.query.filter_by(email=data["email"]).first():
                return jsonify(
                    {"success": False, "message": "Email already exists"}
                ), 400
            user.email = data["email"]

        if "fullName" in data:
            user.full_name = data["fullName"]

        if "department" in data:
            user.department = data["department"]

        if "position" in data:
            user.position = data["position"]

        db.session.commit()

        # Log operation
        log = OperationLog(
            user_id=user_id,
            operation_type=OperationType.UPDATE.value,
            target_type="user_profile",
            target_id=user.id,
            target_description=f"Updated profile for {user.username}",
            operation_description="User updated their profile",
            old_data=json.dumps(old_data),
            new_data=json.dumps(user.to_dict()),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            success=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Profile updated successfully",
                "data": {"user": user.to_dict()},
            }
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating user profile: {str(e)}")
        return jsonify(
            {"success": False, "message": "Failed to update profile", "error": str(e)}
        ), 500


@user_bp.route("/password", methods=["PUT"])
@jwt_required()
def change_password():
    """Change the current user's password.
    ---
    tags:
      - Users
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - currentPassword
              - newPassword
            properties:
              currentPassword:
                type: string
                format: password
                description: Current password
              newPassword:
                type: string
                format: password
                description: New password
    responses:
      200:
        description: Password changed successfully
      400:
        description: Invalid request data
      401:
        description: Unauthorized or incorrect current password
      404:
        description: User not found
      500:
        description: Internal server error
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        data = request.json

        # Validate required fields
        required_fields = ["currentPassword", "newPassword"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify(
                    {"success": False, "message": f"Missing required field: {field}"}
                ), 400

        # Verify current password
        if not user.check_password(data["currentPassword"]):
            return jsonify(
                {"success": False, "message": "Current password is incorrect"}
            ), 401

        # Update password
        user.set_password(data["newPassword"])
        db.session.commit()

        # Log operation
        log = OperationLog(
            user_id=user_id,
            operation_type=OperationType.UPDATE.value,
            target_type="user_password",
            target_id=user.id,
            target_description=f"Changed password for {user.username}",
            operation_description="User changed their password",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            success=True,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({"success": True, "message": "Password changed successfully"})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error changing password: {str(e)}")
        return jsonify(
            {"success": False, "message": "Failed to change password", "error": str(e)}
        ), 500

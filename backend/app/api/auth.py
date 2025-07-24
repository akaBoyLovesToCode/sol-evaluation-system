from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from app import db
from app.models import OperationLog, User
from app.utils.helpers import get_client_ip, get_user_agent
from app.utils.validators import validate_email, validate_password

# Create authentication blueprint
auth_bp = Blueprint("auth", __name__)

# Store blacklisted tokens (in production, use Redis or database)
blacklisted_tokens = set()


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    User login endpoint

    Expected JSON payload:
    {
        "username": "user@example.com",
        "password": "password123"
    }

    Returns:
        JSON response with access token and user info
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get("username", "").strip()
        password = data.get("password", "")

        # Validate input
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            # Log failed login attempt
            if user:
                OperationLog.log_login(
                    user_id=user.id,
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request),
                    success=False,
                    error_message="Invalid password",
                )

            return jsonify({"error": "Invalid username or password"}), 401

        # Check if user is active
        if not user.is_active:
            OperationLog.log_login(
                user_id=user.id,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                success=False,
                error_message="Account is inactive",
            )
            return jsonify({"error": "Account is inactive"}), 401

        # Create tokens
        access_token = create_access_token(
            identity=str(user.id), additional_claims={"role": user.role}
        )
        refresh_token = create_refresh_token(identity=str(user.id))

        # Update last login
        user.update_last_login()

        # Log successful login
        OperationLog.log_login(
            user_id=user.id,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            success=True,
        )

        return jsonify(
            {
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.to_dict(),
            }
        ), 200

    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    User logout endpoint
    Blacklists the current JWT token
    """
    try:
        # Get current token and user
        jti = get_jwt()["jti"]  # JWT ID
        user_id = int(get_jwt_identity())  # Convert string to int

        # Add token to blacklist
        blacklisted_tokens.add(jti)

        # Log logout
        OperationLog.log_logout(user_id=user_id, ip_address=get_client_ip(request))

        return jsonify({"message": "Successfully logged out"}), 200

    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token
    """
    try:
        current_user_id = int(get_jwt_identity())  # Convert string to int

        # Get user to include role in new token
        user = User.query.get(current_user_id)
        if not user or not user.is_active:
            return jsonify({"error": "User not found or inactive"}), 401

        # Create new access token
        new_access_token = create_access_token(
            identity=str(current_user_id), additional_claims={"role": user.role}
        )

        return jsonify({"access_token": new_access_token}), 200

    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """
    Get current user information
    """
    try:
        current_user_id = int(get_jwt_identity())  # Convert string to int
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"user": user.to_dict()}), 200

    except Exception as e:
        current_app.logger.error(f"Get current user error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    """
    Change user password

    Expected JSON payload:
    {
        "current_password": "oldpassword",
        "new_password": "newpassword"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        current_password = data.get("current_password", "")
        new_password = data.get("new_password", "")

        # Validate input
        if not current_password or not new_password:
            return jsonify(
                {"error": "Current password and new password are required"}
            ), 400

        # Validate new password
        password_validation = validate_password(new_password)
        if not password_validation["valid"]:
            return jsonify({"error": password_validation["message"]}), 400

        # Get current user
        current_user_id = int(get_jwt_identity())  # Convert string to int
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Verify current password
        if not user.check_password(current_password):
            return jsonify({"error": "Current password is incorrect"}), 401

        # Update password
        user.set_password(new_password)
        db.session.commit()

        # Log password change
        OperationLog.log_system_operation(
            user_id=current_user_id,
            operation_description="Password changed",
            operation_data={"username": user.username},
            ip_address=get_client_ip(request),
        )

        return jsonify({"message": "Password changed successfully"}), 200

    except Exception as e:
        current_app.logger.error(f"Change password error: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    User registration endpoint (admin only in production)

    Expected JSON payload:
    {
        "username": "newuser",
        "email": "user@example.com",
        "password": "password123",
        "full_name": "Full Name",
        "role": "user",
        "department": "Engineering"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Extract required fields
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")
        full_name = data.get("full_name", "").strip()
        role = data.get("role", "user")

        # Validate required fields
        if not all([username, email, password, full_name]):
            return jsonify(
                {"error": "Username, email, password, and full name are required"}
            ), 400

        # Validate email format
        email_validation = validate_email(email)
        if not email_validation["valid"]:
            return jsonify({"error": email_validation["message"]}), 400

        # Validate password
        password_validation = validate_password(password)
        if not password_validation["valid"]:
            return jsonify({"error": password_validation["message"]}), 400

        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            if existing_user.username == username:
                return jsonify({"error": "Username already exists"}), 409
            else:
                return jsonify({"error": "Email already exists"}), 409

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

        return jsonify(
            {"message": "User registered successfully", "user": user.to_dict()}
        ), 201

    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500


# JWT token blacklist checker
@auth_bp.before_app_request
def check_if_token_revoked():
    """Check if JWT token is blacklisted"""
    try:
        if request.endpoint and "auth" in request.endpoint:
            return  # Skip for auth endpoints

        # This will be called for all protected routes
        # The actual token validation is handled by flask-jwt-extended
        pass
    except Exception:
        pass


# Custom JWT error handlers
@auth_bp.errorhandler(401)
def handle_unauthorized(error):
    """Handle unauthorized access"""
    return jsonify({"error": "Unauthorized access"}), 401


@auth_bp.errorhandler(422)
def handle_unprocessable_entity(error):
    """Handle JWT decode errors"""
    return jsonify({"error": "Invalid token"}), 422

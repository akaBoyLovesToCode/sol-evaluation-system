from functools import wraps
from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt
from app.models import User, OperationLog
from app.utils.helpers import get_client_ip, get_current_user_id


def require_role(required_role):
    """
    Decorator to require specific user role for endpoint access

    Args:
        required_role (str): Required role ('admin', 'group_leader', 'part_leader', 'user')

    Returns:
        function: Decorated function
    """

    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_current_user_id()
                user = User.query.get(current_user_id)

                if not user:
                    return jsonify({"error": "User not found"}), 404

                if not user.is_active:
                    return jsonify({"error": "Account is inactive"}), 401

                if not user.has_permission(required_role):
                    return jsonify({"error": "Insufficient permissions"}), 403

                return f(*args, **kwargs)

            except Exception as e:
                current_app.logger.error(f"Role check error: {str(e)}")
                return jsonify({"error": "Authorization error"}), 500

        return decorated_function

    return decorator


def require_admin(f):
    """
    Decorator to require admin role
    Shortcut for @require_role('admin')
    """
    return require_role("admin")(f)


def require_group_leader(f):
    """
    Decorator to require group leader role or higher
    Shortcut for @require_role('group_leader')
    """
    return require_role("group_leader")(f)


def require_part_leader(f):
    """
    Decorator to require part leader role or higher
    Shortcut for @require_role('part_leader')
    """
    return require_role("part_leader")(f)


def role_required(allowed_roles):
    """
    Decorator to require one of the specified roles

    Args:
        allowed_roles (list): List of allowed roles

    Returns:
        function: Decorated function
    """

    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_current_user_id()
                user = User.query.get(current_user_id)

                if not user:
                    return jsonify({"error": "User not found"}), 404

                if not user.is_active:
                    return jsonify({"error": "Account is inactive"}), 401

                # Convert role names to lowercase for comparison
                user_role = user.role.lower()
                allowed_roles_lower = [
                    role.lower().replace(" ", "_") for role in allowed_roles
                ]

                # Map display names to database values
                role_mapping = {
                    "admin": "admin",
                    "group_leader": "group_leader",
                    "part_leader": "part_leader",
                    "user": "user",
                }

                # Check if user has any of the allowed roles
                has_permission = False
                for allowed_role in allowed_roles_lower:
                    mapped_role = role_mapping.get(allowed_role, allowed_role)
                    if user.has_permission(mapped_role):
                        has_permission = True
                        break

                if not has_permission:
                    return jsonify({"error": "Insufficient permissions"}), 403

                return f(*args, **kwargs)

            except Exception as e:
                current_app.logger.error(f"Role check error: {str(e)}")
                return jsonify({"error": "Authorization error"}), 500

        return decorated_function

    return decorator


def log_operation(operation_type, target_type, get_target_id=None, get_old_data=None):
    """
    Decorator to automatically log operations

    Args:
        operation_type (str): Type of operation ('create', 'update', 'delete', etc.)
        target_type (str): Type of target ('evaluation', 'user', etc.)
        get_target_id (function): Function to extract target ID from response
        get_old_data (function): Function to get old data before operation

    Returns:
        function: Decorated function
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get old data before operation (if function provided)
            old_data = None
            if get_old_data:
                try:
                    old_data = get_old_data(*args, **kwargs)
                except Exception as e:
                    current_app.logger.warning(f"Failed to get old data: {str(e)}")

            # Execute the original function
            result = f(*args, **kwargs)

            # Log the operation after successful execution
            try:
                current_user_id = get_current_user_id()
                if current_user_id:
                    # Extract target ID from result if function provided
                    target_id = None
                    if get_target_id and isinstance(result, tuple) and len(result) >= 2:
                        response_data = result[0]
                        if isinstance(response_data, dict):
                            target_id = get_target_id(response_data)

                    # Create operation log
                    OperationLog(
                        user_id=current_user_id,
                        operation_type=operation_type,
                        target_type=target_type,
                        target_id=target_id,
                        operation_description=f"{operation_type.title()} {target_type}",
                        old_data=old_data,
                        ip_address=get_client_ip(request),
                        success=True,
                    )

            except Exception as e:
                current_app.logger.error(f"Operation logging error: {str(e)}")
                # Don't fail the request if logging fails

            return result

        return decorated_function

    return decorator


def handle_exceptions(f):
    """
    Decorator to handle common exceptions and return standardized error responses
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            current_app.logger.warning(f"Validation error in {f.__name__}: {str(e)}")
            return jsonify({"error": str(e)}), 400
        except PermissionError as e:
            current_app.logger.warning(f"Permission error in {f.__name__}: {str(e)}")
            return jsonify({"error": "Permission denied"}), 403
        except FileNotFoundError as e:
            current_app.logger.warning(f"File not found in {f.__name__}: {str(e)}")
            return jsonify({"error": "Resource not found"}), 404
        except Exception as e:
            current_app.logger.error(f"Unexpected error in {f.__name__}: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    return decorated_function


def validate_json(required_fields=None, optional_fields=None):
    """
    Decorator to validate JSON request data

    Args:
        required_fields (list): List of required field names
        optional_fields (list): List of optional field names

    Returns:
        function: Decorated function
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400

            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400

            # Check required fields
            if required_fields:
                missing_fields = []
                for field in required_fields:
                    if field not in data or data[field] is None or data[field] == "":
                        missing_fields.append(field)

                if missing_fields:
                    return jsonify(
                        {
                            "error": f"Missing required fields: {', '.join(missing_fields)}"
                        }
                    ), 400

            # Check for unexpected fields (if optional_fields is provided)
            if optional_fields is not None:
                allowed_fields = set(required_fields or []) | set(optional_fields)
                unexpected_fields = set(data.keys()) - allowed_fields

                if unexpected_fields:
                    return jsonify(
                        {"error": f"Unexpected fields: {', '.join(unexpected_fields)}"}
                    ), 400

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def rate_limit(max_requests=100, window_seconds=3600):
    """
    Simple rate limiting decorator (in production, use Redis-based solution)

    Args:
        max_requests (int): Maximum requests allowed
        window_seconds (int): Time window in seconds

    Returns:
        function: Decorated function
    """
    # Simple in-memory storage (not suitable for production)
    request_counts = {}

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from datetime import datetime, timedelta

            # Get client identifier
            client_ip = get_client_ip(request)
            current_user_id = None

            try:
                current_user_id = get_current_user_id()
            except:
                pass

            client_id = (
                f"{client_ip}:{current_user_id}" if current_user_id else client_ip
            )

            now = datetime.utcnow()
            window_start = now - timedelta(seconds=window_seconds)

            # Clean old entries
            if client_id in request_counts:
                request_counts[client_id] = [
                    timestamp
                    for timestamp in request_counts[client_id]
                    if timestamp > window_start
                ]
            else:
                request_counts[client_id] = []

            # Check rate limit
            if len(request_counts[client_id]) >= max_requests:
                return jsonify(
                    {"error": "Rate limit exceeded", "retry_after": window_seconds}
                ), 429

            # Add current request
            request_counts[client_id].append(now)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def cache_response(timeout=300):
    """
    Simple response caching decorator (in production, use Redis)

    Args:
        timeout (int): Cache timeout in seconds

    Returns:
        function: Decorated function
    """
    # Simple in-memory cache (not suitable for production)
    cache = {}

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from datetime import datetime, timedelta
            import hashlib
            import json

            # Create cache key from function name, args, and request data
            user_id = None
            try:
                user_id = (
                    get_current_user_id()
                    if request.headers.get("Authorization")
                    else None
                )
            except:
                pass  # Ignore JWT errors for caching

            cache_key_data = {
                "function": f.__name__,
                "args": str(args),
                "kwargs": str(kwargs),
                "query_string": request.query_string.decode(),
                "user_id": user_id,
            }

            cache_key = hashlib.md5(
                json.dumps(cache_key_data, sort_keys=True).encode()
            ).hexdigest()

            now = datetime.utcnow()

            # Check if cached response exists and is still valid
            if cache_key in cache:
                cached_response, cached_time = cache[cache_key]
                if now - cached_time < timedelta(seconds=timeout):
                    return cached_response

            # Execute function and cache result
            result = f(*args, **kwargs)
            cache[cache_key] = (result, now)

            # Clean old cache entries (simple cleanup)
            if len(cache) > 1000:  # Arbitrary limit
                cutoff_time = now - timedelta(seconds=timeout)
                cache = {k: v for k, v in cache.items() if v[1] > cutoff_time}

            return result

        return decorated_function

    return decorator

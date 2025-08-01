"""Helper utility functions for the Product Evaluation System."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, date
from typing import Optional, Any, Dict, List, Tuple, Union

from flask import Request
from flask_jwt_extended import get_jwt_identity
from app.models import SystemConfig


def get_current_user_id() -> Optional[int]:
    """Get current user ID from JWT token, converting from string to int.

    Returns:
        Current user ID or None if not authenticated.

    """
    try:
        identity = get_jwt_identity()
        return int(identity) if identity else None
    except (ValueError, TypeError):
        return None


def get_client_ip(request: Request) -> Optional[str]:
    """Get client IP address from request.

    Args:
        request: Flask request object.

    Returns:
        Client IP address.

    """
    # Check for forwarded IP (when behind proxy/load balancer)
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    elif request.headers.get("X-Real-IP"):
        return request.headers.get("X-Real-IP")
    else:
        return request.remote_addr


def get_user_agent(request: Request) -> str:
    """Get user agent string from request.

    Args:
        request: Flask request object.

    Returns:
        User agent string.

    """
    return request.headers.get("User-Agent", "Unknown")


def generate_evaluation_number() -> str:
    """Generate unique evaluation number.

    Returns:
        Unique evaluation number in format PREFIX-YYYYMMDD-XXXX.

    """
    # Get prefix from system config
    prefix = SystemConfig.get_config("evaluation_number_prefix", "EVAL")

    # Get current date
    date_str = datetime.now().strftime("%Y%m%d")

    # Generate unique suffix (last 4 characters of UUID)
    unique_suffix = str(uuid.uuid4()).replace("-", "")[-4:].upper()

    return f"{prefix}-{date_str}-{unique_suffix}"


def format_datetime(dt: Optional[datetime], format_string: Optional[str] = None) -> Optional[str]:
    """Format datetime object to string.

    Args:
        dt: Datetime object to format.
        format_string: Format string (optional).

    Returns:
        Formatted datetime string.

    """
    if not dt:
        return None

    if not format_string:
        format_string = "%Y-%m-%d %H:%M:%S"

    return dt.strftime(format_string)


def format_date(date_obj: Optional[date], format_string: Optional[str] = None) -> Optional[str]:
    """Format date object to string.

    Args:
        date_obj: Date object to format.
        format_string: Format string (optional).

    Returns:
        Formatted date string.

    """
    if not date_obj:
        return None

    if not format_string:
        format_string = "%Y-%m-%d"

    return date_obj.strftime(format_string)


def parse_date_string(date_string: Optional[str], format_string: str = "%Y-%m-%d") -> Optional[date]:
    """Parse date string to date object.

    Args:
        date_string: Date string to parse.
        format_string: Expected format string.

    Returns:
        Parsed date object or None if parsing fails.

    """
    if not date_string:
        return None

    try:
        return datetime.strptime(date_string, format_string).date()
    except ValueError:
        return None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations.

    Args:
        filename: Original filename.

    Returns:
        Sanitized filename.

    """
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Remove leading/trailing spaces and dots
    filename = filename.strip(" .")

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        max_name_length = 255 - len(ext) - 1 if ext else 255
        filename = name[:max_name_length] + ("." + ext if ext else "")

    return filename


def calculate_pagination(page: int, per_page: int, total_count: int) -> Dict[str, Any]:
    """Calculate pagination information.

    Args:
        page: Current page number (1-based).
        per_page: Items per page.
        total_count: Total number of items.

    Returns:
        Pagination information dictionary.

    """
    if page < 1:
        page = 1

    if per_page < 1:
        per_page = SystemConfig.get_config("items_per_page", 20)

    total_pages = (total_count + per_page - 1) // per_page

    if page > total_pages and total_pages > 0:
        page = total_pages

    offset = (page - 1) * per_page

    return {
        "page": page,
        "per_page": per_page,
        "total_count": total_count,
        "total_pages": total_pages,
        "offset": offset,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_page": page - 1 if page > 1 else None,
        "next_page": page + 1 if page < total_pages else None,
    }


def build_query_filters(model: Any, filters: Dict[str, Any]) -> List[Any]:
    """Build SQLAlchemy query filters from dictionary.

    Args:
        model: SQLAlchemy model class.
        filters: Filter parameters.

    Returns:
        List of filter conditions.

    """
    conditions = []

    for field, value in filters.items():
        if value is None or value == "":
            continue

        if hasattr(model, field):
            column = getattr(model, field)

            # Handle different filter types
            if isinstance(value, dict):
                # Range filters
                if "gte" in value:
                    conditions.append(column >= value["gte"])
                if "lte" in value:
                    conditions.append(column <= value["lte"])
                if "gt" in value:
                    conditions.append(column > value["gt"])
                if "lt" in value:
                    conditions.append(column < value["lt"])
                if "in" in value and isinstance(value["in"], list):
                    conditions.append(column.in_(value["in"]))
                if "like" in value:
                    conditions.append(column.like(f"%{value['like']}%"))
            elif isinstance(value, list):
                # IN filter
                conditions.append(column.in_(value))
            else:
                # Exact match
                conditions.append(column == value)

    return conditions


def get_enum_values(enum_column: Any) -> List[str]:
    """Get possible values for an enum column.

    Args:
        enum_column: SQLAlchemy enum column.

    Returns:
        List of possible enum values.

    """
    try:
        return [e.name for e in enum_column.type.enums]
    except AttributeError:
        return []


def create_response(
    data: Optional[Any] = None,
    message: Optional[str] = None,
    status_code: int = 200,
    errors: Optional[Any] = None,
) -> Tuple[Dict[str, Any], int]:
    """Create standardized API response.

    Args:
        data: Response data.
        message: Response message.
        status_code: HTTP status code.
        errors: Error information.

    Returns:
        Tuple of (response_dict, status_code).

    """
    response: Dict[str, Any] = {}

    if data is not None:
        response["data"] = data

    if message:
        response["message"] = message

    if errors:
        response["errors"] = errors

    response["success"] = status_code < 400
    response["timestamp"] = datetime.utcnow().isoformat()

    return response, status_code


def mask_sensitive_data(data: Dict[str, Any], sensitive_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """Mask sensitive data in dictionary.

    Args:
        data: Data dictionary.
        sensitive_fields: List of sensitive field names.

    Returns:
        Data with sensitive fields masked.

    """
    if sensitive_fields is None:
        sensitive_fields = ["password", "password_hash", "token", "secret"]

    if not isinstance(data, dict):
        return data

    masked_data = data.copy()

    for field in sensitive_fields:
        if field in masked_data:
            masked_data[field] = "***masked***"

    return masked_data

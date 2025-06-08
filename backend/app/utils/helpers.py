from datetime import datetime
import uuid
from flask_jwt_extended import get_jwt_identity
from app.models import SystemConfig

def get_current_user_id():
    """
    Get current user ID from JWT token, converting from string to int
    
    Returns:
        int: Current user ID or None if not authenticated
    """
    try:
        identity = get_jwt_identity()
        return int(identity) if identity else None
    except (ValueError, TypeError):
        return None

def get_client_ip(request):
    """
    Get client IP address from request
    
    Args:
        request: Flask request object
        
    Returns:
        str: Client IP address
    """
    # Check for forwarded IP (when behind proxy/load balancer)
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def get_user_agent(request):
    """
    Get user agent string from request
    
    Args:
        request: Flask request object
        
    Returns:
        str: User agent string
    """
    return request.headers.get('User-Agent', 'Unknown')

def generate_evaluation_number():
    """
    Generate unique evaluation number
    
    Returns:
        str: Unique evaluation number in format PREFIX-YYYYMMDD-XXXX
    """
    # Get prefix from system config
    prefix = SystemConfig.get_config('evaluation_number_prefix', 'EVAL')
    
    # Get current date
    date_str = datetime.now().strftime('%Y%m%d')
    
    # Generate unique suffix (last 4 characters of UUID)
    unique_suffix = str(uuid.uuid4()).replace('-', '')[-4:].upper()
    
    return f'{prefix}-{date_str}-{unique_suffix}'

def format_datetime(dt, format_string=None):
    """
    Format datetime object to string
    
    Args:
        dt (datetime): Datetime object to format
        format_string (str): Format string (optional)
        
    Returns:
        str: Formatted datetime string
    """
    if not dt:
        return None
    
    if not format_string:
        format_string = '%Y-%m-%d %H:%M:%S'
    
    return dt.strftime(format_string)

def format_date(date_obj, format_string=None):
    """
    Format date object to string
    
    Args:
        date_obj (date): Date object to format
        format_string (str): Format string (optional)
        
    Returns:
        str: Formatted date string
    """
    if not date_obj:
        return None
    
    if not format_string:
        format_string = '%Y-%m-%d'
    
    return date_obj.strftime(format_string)

def parse_date_string(date_string, format_string='%Y-%m-%d'):
    """
    Parse date string to date object
    
    Args:
        date_string (str): Date string to parse
        format_string (str): Expected format string
        
    Returns:
        date: Parsed date object or None if parsing fails
    """
    if not date_string:
        return None
    
    try:
        return datetime.strptime(date_string, format_string).date()
    except ValueError:
        return None

def sanitize_filename(filename):
    """
    Sanitize filename for safe file operations
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    import re
    
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_length = 255 - len(ext) - 1 if ext else 255
        filename = name[:max_name_length] + ('.' + ext if ext else '')
    
    return filename

def calculate_pagination(page, per_page, total_count):
    """
    Calculate pagination information
    
    Args:
        page (int): Current page number (1-based)
        per_page (int): Items per page
        total_count (int): Total number of items
        
    Returns:
        dict: Pagination information
    """
    if page < 1:
        page = 1
    
    if per_page < 1:
        per_page = SystemConfig.get_config('items_per_page', 20)
    
    total_pages = (total_count + per_page - 1) // per_page
    
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    offset = (page - 1) * per_page
    
    return {
        'page': page,
        'per_page': per_page,
        'total_count': total_count,
        'total_pages': total_pages,
        'offset': offset,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None
    }

def build_query_filters(model, filters):
    """
    Build SQLAlchemy query filters from dictionary
    
    Args:
        model: SQLAlchemy model class
        filters (dict): Filter parameters
        
    Returns:
        list: List of filter conditions
    """
    conditions = []
    
    for field, value in filters.items():
        if value is None or value == '':
            continue
        
        if hasattr(model, field):
            column = getattr(model, field)
            
            # Handle different filter types
            if isinstance(value, dict):
                # Range filters
                if 'gte' in value:
                    conditions.append(column >= value['gte'])
                if 'lte' in value:
                    conditions.append(column <= value['lte'])
                if 'gt' in value:
                    conditions.append(column > value['gt'])
                if 'lt' in value:
                    conditions.append(column < value['lt'])
                if 'in' in value and isinstance(value['in'], list):
                    conditions.append(column.in_(value['in']))
                if 'like' in value:
                    conditions.append(column.like(f"%{value['like']}%"))
            elif isinstance(value, list):
                # IN filter
                conditions.append(column.in_(value))
            else:
                # Exact match
                conditions.append(column == value)
    
    return conditions

def get_enum_values(enum_column):
    """
    Get possible values for an enum column
    
    Args:
        enum_column: SQLAlchemy enum column
        
    Returns:
        list: List of possible enum values
    """
    try:
        return [e.name for e in enum_column.type.enums]
    except AttributeError:
        return []

def create_response(data=None, message=None, status_code=200, errors=None):
    """
    Create standardized API response
    
    Args:
        data: Response data
        message (str): Response message
        status_code (int): HTTP status code
        errors: Error information
        
    Returns:
        tuple: (response_dict, status_code)
    """
    response = {}
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    if errors:
        response['errors'] = errors
    
    response['success'] = status_code < 400
    response['timestamp'] = datetime.utcnow().isoformat()
    
    return response, status_code

def mask_sensitive_data(data, sensitive_fields=None):
    """
    Mask sensitive data in dictionary
    
    Args:
        data (dict): Data dictionary
        sensitive_fields (list): List of sensitive field names
        
    Returns:
        dict: Data with sensitive fields masked
    """
    if sensitive_fields is None:
        sensitive_fields = ['password', 'password_hash', 'token', 'secret']
    
    if not isinstance(data, dict):
        return data
    
    masked_data = data.copy()
    
    for field in sensitive_fields:
        if field in masked_data:
            masked_data[field] = '***masked***'
    
    return masked_data 
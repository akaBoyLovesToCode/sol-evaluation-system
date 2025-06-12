import re
from app.models import SystemConfig


def validate_email(email):
    """
    Validate email address format

    Args:
        email (str): Email address to validate

    Returns:
        dict: Validation result with 'valid' boolean and 'message' string
    """
    if not email:
        return {"valid": False, "message": "Email is required"}

    # Basic email regex pattern
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(email_pattern, email):
        return {"valid": False, "message": "Invalid email format"}

    if len(email) > 120:
        return {
            "valid": False,
            "message": "Email address is too long (max 120 characters)",
        }

    return {"valid": True, "message": "Valid email"}


def validate_password(password):
    """
    Validate password strength

    Args:
        password (str): Password to validate

    Returns:
        dict: Validation result with 'valid' boolean and 'message' string
    """
    if not password:
        return {"valid": False, "message": "Password is required"}

    # Get minimum password length from system config
    min_length = SystemConfig.get_config("password_min_length", 8)

    if len(password) < min_length:
        return {
            "valid": False,
            "message": f"Password must be at least {min_length} characters long",
        }

    if len(password) > 128:
        return {"valid": False, "message": "Password is too long (max 128 characters)"}

    # Check for at least one letter
    if not re.search(r"[a-zA-Z]", password):
        return {"valid": False, "message": "Password must contain at least one letter"}

    # Check for at least one number
    if not re.search(r"\d", password):
        return {"valid": False, "message": "Password must contain at least one number"}

    return {"valid": True, "message": "Valid password"}


def validate_username(username):
    """
    Validate username format

    Args:
        username (str): Username to validate

    Returns:
        dict: Validation result with 'valid' boolean and 'message' string
    """
    if not username:
        return {"valid": False, "message": "Username is required"}

    if len(username) < 3:
        return {
            "valid": False,
            "message": "Username must be at least 3 characters long",
        }

    if len(username) > 80:
        return {"valid": False, "message": "Username is too long (max 80 characters)"}

    # Username can contain letters, numbers, underscores, and hyphens
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return {
            "valid": False,
            "message": "Username can only contain letters, numbers, underscores, and hyphens",
        }

    return {"valid": True, "message": "Valid username"}


def validate_evaluation_data(data, evaluation_type):
    """
    Validate evaluation data based on type

    Args:
        data (dict): Evaluation data to validate
        evaluation_type (str): Type of evaluation ('new_product' or 'mass_production')

    Returns:
        dict: Validation result with 'valid' boolean and 'errors' list
    """
    errors = []

    # Required fields for all evaluations
    required_fields = ["product_name", "part_number", "start_date"]

    for field in required_fields:
        if not data.get(field):
            errors.append(f"{field.replace('_', ' ').title()} is required")

    # Validate product name
    product_name = data.get("product_name", data.get("ssd_product", "")).strip()
    if product_name and len(product_name) > 100:
        errors.append("Product name is too long (max 100 characters)")

    # Validate part number
    part_number = data.get("part_number", "").strip()
    if part_number and len(part_number) > 50:
        errors.append("Part number is too long (max 50 characters)")

    # Validate evaluation reason
    evaluation_reason = data.get("evaluation_reason", "").strip()
    if evaluation_reason and len(evaluation_reason) > 1000:
        errors.append("Evaluation reason is too long (max 1000 characters)")

    # Validate remarks
    remarks = data.get("remarks", "").strip()
    if remarks and len(remarks) > 1000:
        errors.append("Remarks is too long (max 1000 characters)")

    # Type-specific validations
    if evaluation_type == "new_product":
        # New product evaluations may have additional requirements
        pass
    elif evaluation_type == "mass_production":
        # Mass production evaluations may have different requirements
        pass

    return {"valid": len(errors) == 0, "errors": errors}


def validate_evaluation_detail(detail_data, detail_type):
    """
    Validate evaluation detail data based on type

    Args:
        detail_data (dict): Detail data to validate
        detail_type (str): Type of detail ('pgm', 'material', 'equipment')

    Returns:
        dict: Validation result with 'valid' boolean and 'errors' list
    """
    errors = []

    if detail_type == "pgm":
        # PGM evaluations require version information
        if not detail_data.get("pgm_version_before"):
            errors.append("PGM version before is required")
        if not detail_data.get("pgm_version_after"):
            errors.append("PGM version after is required")

        # Validate version format (optional - can be customized)
        for field in ["pgm_version_before", "pgm_version_after"]:
            version = detail_data.get(field, "").strip()
            if version and len(version) > 50:
                errors.append(
                    f"{field.replace('_', ' ').title()} is too long (max 50 characters)"
                )

    elif detail_type == "material":
        # Material evaluations require material information
        if not detail_data.get("material_name"):
            errors.append("Material name is required")
        if not detail_data.get("material_number"):
            errors.append("Material number is required")

        # Validate material fields
        material_name = detail_data.get("material_name", "").strip()
        if material_name and len(material_name) > 100:
            errors.append("Material name is too long (max 100 characters)")

        material_number = detail_data.get("material_number", "").strip()
        if material_number and len(material_number) > 50:
            errors.append("Material number is too long (max 50 characters)")

    elif detail_type == "equipment":
        # Equipment evaluations require equipment information
        if not detail_data.get("equipment_name"):
            errors.append("Equipment name is required")
        if not detail_data.get("equipment_number"):
            errors.append("Equipment number is required")

        # Validate equipment fields
        equipment_name = detail_data.get("equipment_name", "").strip()
        if equipment_name and len(equipment_name) > 100:
            errors.append("Equipment name is too long (max 100 characters)")

        equipment_number = detail_data.get("equipment_number", "").strip()
        if equipment_number and len(equipment_number) > 50:
            errors.append("Equipment number is too long (max 50 characters)")

    return {"valid": len(errors) == 0, "errors": errors}


def validate_date_range(start_date, end_date):
    """
    Validate date range

    Args:
        start_date (date): Start date
        end_date (date): End date

    Returns:
        dict: Validation result with 'valid' boolean and 'message' string
    """
    if not start_date:
        return {"valid": False, "message": "Start date is required"}

    if end_date and start_date > end_date:
        return {"valid": False, "message": "Start date cannot be after end date"}

    return {"valid": True, "message": "Valid date range"}

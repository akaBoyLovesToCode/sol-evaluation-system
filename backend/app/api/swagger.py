"""
Swagger API documentation configuration.
"""

from flask import Blueprint, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

# Create a Blueprint for the Swagger API
swagger_bp = Blueprint("swagger", __name__)

# Create an APISpec
spec = APISpec(
    title="Product Evaluation API",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
    info=dict(
        description="API for Product Evaluation Management System",
        contact=dict(email="admin@example.com"),
    ),
)

# Define the Swagger UI Blueprint
SWAGGER_URL = "/api/docs"  # URL for exposing Swagger UI
API_URL = "/api/swagger.json"  # URL for the Swagger JSON documentation

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Product Evaluation API"}
)


# Route to serve the Swagger JSON
@swagger_bp.route("/swagger.json")
def swagger_json():
    """Serve the Swagger JSON specification."""
    return jsonify(spec.to_dict())


# Function to register all API routes with Swagger
def register_api_routes(app):
    """
    Register all API routes with Swagger.

    Args:
        app: Flask application instance
    """
    # Import API modules to ensure they are registered with Swagger
    from app.api import evaluation, auth, user, operation_log

    # Register the Swagger blueprints
    app.register_blueprint(swagger_bp, url_prefix="/api")
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Add security schemes
    spec.components.security_scheme(
        "bearerAuth", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    )

    # Add tags for API organization
    spec.tag({"name": "Authentication", "description": "Authentication operations"})
    spec.tag({"name": "Evaluations", "description": "Evaluation management operations"})
    spec.tag({"name": "Users", "description": "User management operations"})
    spec.tag(
        {"name": "Operation Logs", "description": "Operation logging and audit trail"}
    )

    # Register all routes with Swagger
    with app.test_request_context():
        for rule in app.url_map.iter_rules():
            if rule.endpoint != "static" and not rule.rule.startswith("/api/docs"):
                spec.path(view=app.view_functions[rule.endpoint])

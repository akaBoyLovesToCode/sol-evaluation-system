"""Product Evaluation System Flask Application Factory."""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Any

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
socketio = SocketIO()


def init_tracing() -> None:
    """Initialize OpenTelemetry tracing for observability."""
    # Set up tracer provider
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer_provider()

    # Configure Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name=os.getenv("JAEGER_HOST", "localhost"),
        agent_port=int(os.getenv("JAEGER_PORT", "6831")),
    )

    # Add batch span processor
    span_processor = BatchSpanProcessor(jaeger_exporter)
    tracer.add_span_processor(span_processor)


def create_app(config_name: str | None = None) -> Flask:
    """Application factory pattern for creating Flask app.

    Args:
        config_name: Configuration name ('development', 'production', 'testing').

    Returns:
        Configured Flask application instance.

    """
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    from config import config

    app.config.from_object(config[config_name])

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Debug CORS configuration
    cors_origins = app.config["CORS_ORIGINS"]
    app.logger.info(f"Flask app CORS_ORIGINS configuration: {cors_origins}")

    # Initialize CORS with comprehensive settings
    cors.init_app(
        app,
        origins=cors_origins,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )
    socketio.init_app(app, cors_allowed_origins=cors_origins)

    # Initialize OpenTelemetry tracing
    if os.getenv("ENABLE_TRACING", "false").lower() == "true":
        init_tracing()
        FlaskInstrumentor().instrument_app(app)
        SQLAlchemyInstrumentor().instrument(engine=db.engine)

    # Register blueprints
    from app.api import auth_bp, dashboard_bp, evaluation_bp, operation_log_bp, user_bp
    from app.api.notifications import notifications_bp
    from app.api.swagger import register_api_routes
    from app.api.workflow import workflow_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(evaluation_bp, url_prefix="/api/evaluations")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(workflow_bp, url_prefix="/api/workflow")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")
    app.register_blueprint(operation_log_bp, url_prefix="/api/logs")

    # Register Swagger API documentation
    register_api_routes(app)

    # Configure logging
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        logs_dir = os.path.dirname(app.config["LOG_FILE"])
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        # Set up file handler with rotation
        file_handler = RotatingFileHandler(
            app.config["LOG_FILE"],
            maxBytes=10240000,  # 10MB
            backupCount=10,
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Product Evaluation System startup")

    # Create upload and backup directories
    for directory in [app.config["UPLOAD_FOLDER"], app.config["BACKUP_FOLDER"]]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error: Any) -> tuple[dict[str, str], int]:
        """Handle 404 not found errors."""
        return {"error": "Resource not found"}, 404

    @app.errorhandler(500)
    def internal_error(error: Any) -> tuple[dict[str, str], int]:
        """Handle 500 internal server errors."""
        db.session.rollback()
        return {"error": "Internal server error"}, 500

    # Health check endpoint
    @app.route("/api/health")
    def health_check() -> dict[str, str]:
        """Health check endpoint for monitoring."""
        return {"status": "healthy", "message": "Product Evaluation System is running"}

    # Debug CORS endpoint
    @app.route("/api/debug/cors")
    def debug_cors() -> dict[str, any]:
        """Debug endpoint to check CORS configuration."""
        return {
            "cors_origins": app.config.get("CORS_ORIGINS", []),
            "cors_origins_env": os.environ.get("CORS_ORIGINS", "NOT_SET"),
            "all_env_vars": {
                k: v
                for k, v in os.environ.items()
                if "CORS" in k or "FRONTEND" in k or "RAILWAY" in k
            },
        }

    # Auto-initialize database if empty
    with app.app_context():
        try:
            # Check if database is initialized by looking for users table
            from app.models.user import User

            User.query.first()
            app.logger.info("Database already initialized")
        except Exception:
            # Database is empty, create tables and default data
            app.logger.info("Database is empty, initializing...")
            db.create_all()

            # Create default admin user
            from app.models.user import User
            from werkzeug.security import generate_password_hash
            from datetime import datetime

            admin_user = User(
                username="admin",
                email="admin@evaluation.system",
                password_hash=generate_password_hash("admin123"),
                full_name="System Administrator",
                role="admin",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.session.add(admin_user)
            db.session.commit()
            app.logger.info(
                "Database initialized with default admin user (admin/admin123)"
            )

    return app

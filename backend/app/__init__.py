from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import logging
from logging.handlers import RotatingFileHandler

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
socketio = SocketIO()


def create_app(config_name=None):
    """
    Application factory pattern for creating Flask app

    Args:
        config_name (str): Configuration name ('development', 'production', 'testing')

    Returns:
        Flask: Configured Flask application instance
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
    cors.init_app(app, origins=app.config["CORS_ORIGINS"])
    socketio.init_app(app, cors_allowed_origins=app.config["CORS_ORIGINS"])

    # Register blueprints
    from app.api import auth_bp, evaluation_bp, user_bp, dashboard_bp, operation_log_bp
    from app.api.workflow import workflow_bp
    from app.api.notifications import notifications_bp
    from app.api.swagger import register_api_routes

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
    def not_found_error(error):
        return {"error": "Resource not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {"error": "Internal server error"}, 500

    # Health check endpoint
    @app.route("/api/health")
    def health_check():
        """Health check endpoint for monitoring"""
        return {"status": "healthy", "message": "Product Evaluation System is running"}

    return app

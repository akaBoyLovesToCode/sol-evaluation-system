import os
from datetime import timedelta

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_database_uri() -> str:
    """Get database URI based on available environment variables.

    Checks for Railway PostgreSQL DATABASE_URL first, then falls back to
    MySQL configuration for local development.

    Returns:
        str: Database URI for SQLAlchemy connection.

    Note:
        Railway provides postgres:// URLs but SQLAlchemy requires postgresql://.
        This function handles the conversion automatically.
    """
    # Check for Railway PostgreSQL DATABASE_URL first
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        # Railway provides postgres:// but SQLAlchemy needs postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url

    # Fall back to MySQL configuration for development
    mysql_host = os.environ.get("MYSQL_HOST") or "localhost"
    mysql_port = os.environ.get("MYSQL_PORT") or 3306
    mysql_user = os.environ.get("MYSQL_USER") or "root"
    mysql_password = os.environ.get("MYSQL_PASSWORD") or "eval_root_2024"
    mysql_database = os.environ.get("MYSQL_DATABASE") or "evaluation"

    return f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}?charset=utf8mb4"


def get_cors_origins() -> list[str]:
    """Get CORS origins from environment variable or use defaults."""
    import logging

    logger = logging.getLogger(__name__)

    cors_origins_env = os.environ.get("CORS_ORIGINS")
    logger.info(f"Raw CORS_ORIGINS environment variable: {cors_origins_env}")

    if cors_origins_env:
        # Split by comma and strip whitespace
        origins = [origin.strip() for origin in cors_origins_env.split(",")]

        # Fix Railway domains by adding https:// if missing
        fixed_origins = []
        for origin in origins:
            if origin and not origin.startswith(("http://", "https://")):
                # Railway domains need https:// prefix
                if "railway.app" in origin:
                    origin = f"https://{origin}"
                else:
                    # Local development might need http://
                    origin = f"http://{origin}"
            fixed_origins.append(origin)

        logger.info(f"Fixed CORS origins: {fixed_origins}")
        return fixed_origins

    # Fallback: check for Railway frontend domain environment variable
    frontend_domain_env = os.environ.get("VITE_API_BASE_URL")
    if frontend_domain_env and "railway.app" in frontend_domain_env:
        # Extract the base domain and create frontend URL
        frontend_url = "https://frontend-production-d9f6.up.railway.app"
        logger.info(f"Using Railway fallback CORS origin: {frontend_url}")
        return ["http://localhost:3000", "http://localhost:5173", frontend_url]

    # Default origins for development
    default_origins = ["http://localhost:3000", "http://localhost:5173"]
    logger.info(f"Using default CORS origins: {default_origins}")
    return default_origins


class Config:
    """Base configuration class"""

    # Basic Flask configuration
    SECRET_KEY = os.environ.get("SECRET_KEY") or "evaluation-secret-key-2024"

    # Database configuration - supports both MySQL and PostgreSQL
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 20,
        "max_overflow": 0,
    }

    # JWT configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "jwt-secret-string-2024"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_IDENTITY_CLAIM = "sub"  # Explicitly set the identity claim
    JWT_ALGORITHM = "HS256"  # Explicitly set the algorithm

    # CORS configuration
    CORS_ORIGINS = get_cors_origins()

    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")

    # Logging configuration
    LOG_LEVEL = os.environ.get("LOG_LEVEL") or "INFO"
    LOG_FILE = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "logs", "app.log"
    )

    # Pagination
    ITEMS_PER_PAGE = 20

    # Backup configuration
    BACKUP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
    BACKUP_RETENTION_DAYS = 30



class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    TESTING = False

    # Override with production database settings
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or Config.SQLALCHEMY_DATABASE_URI
    )


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

    # Override MySQL-specific engine options for SQLite compatibility
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        # Remove MySQL-specific options that SQLite doesn't support:
        # pool_timeout, max_overflow, pool_recycle
    }


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class"""

    # Basic Flask configuration
    SECRET_KEY = os.environ.get("SECRET_KEY") or "evaluation-secret-key-2024"

    # Database configuration
    MYSQL_HOST = os.environ.get("MYSQL_HOST") or "localhost"
    MYSQL_PORT = os.environ.get("MYSQL_PORT") or 3306
    MYSQL_USER = os.environ.get("MYSQL_USER") or "root"
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD") or "eval_root_2024"
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE") or "evaluation"

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
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
    CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]

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

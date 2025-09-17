#!/usr/bin/env python3
"""Solution Evaluation System - Flask Application Entry Point

This script starts the Flask development server.
For production deployment, use a WSGI server like Gunicorn.
"""

import os

import click
from flask.cli import with_appcontext

from app import create_app, db
from app.models import SystemConfig

# Create Flask application
app = create_app()


@app.cli.command()
@with_appcontext
def init_db():
    """Initialize the database with tables and default data"""
    try:
        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully")

        # Initialize default system configurations
        SystemConfig.initialize_default_configs()
        print("✓ Default system configurations initialized")

        print("\n🎉 Database initialization completed successfully!")
        print("\nNext steps:")
        print("1. Start the application: python run.py")

    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return 1


@app.cli.command()
@with_appcontext
def reset_db():
    """Reset the database (WARNING: This will delete all data!)"""
    if click.confirm("This will delete all data. Are you sure?"):
        try:
            db.drop_all()
            print("✓ All tables dropped")

            db.create_all()
            print("✓ Tables recreated")

            SystemConfig.initialize_default_configs()
            print("✓ Default configurations restored")

            print("🎉 Database reset completed!")

        except Exception as e:
            print(f"❌ Database reset failed: {str(e)}")
            return 1
    else:
        print("Database reset cancelled")


# User management commands removed (auth-less mode)


@app.cli.command()
@with_appcontext
def backup_db():
    """Create a database backup"""
    try:
        import subprocess
        from datetime import datetime

        # Get database configuration
        db_config = app.config
        backup_dir = db_config["BACKUP_FOLDER"]

        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"evaluation_backup_{timestamp}.sql")

        # Create mysqldump command
        cmd = [
            "mysqldump",
            "-h",
            db_config["MYSQL_HOST"],
            "-P",
            str(db_config["MYSQL_PORT"]),
            "-u",
            db_config["MYSQL_USER"],
            f"-p{db_config['MYSQL_PASSWORD']}",
            "--single-transaction",
            "--routines",
            "--triggers",
            db_config["MYSQL_DATABASE"],
        ]

        # Execute backup
        with open(backup_file, "w") as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            print(f"✓ Database backup created: {backup_file}")
        else:
            print(f"❌ Backup failed: {result.stderr}")
            return 1

    except Exception as e:
        print(f"❌ Backup failed: {str(e)}")
        return 1


if __name__ == "__main__":
    # Check if database is initialized
    with app.app_context():
        try:
            # Try to query a table to check if database is set up
            from app.models import SystemConfig

            SystemConfig.query.first()

        except Exception:
            print("⚠️  Database not initialized. Run 'flask init-db' first.")
            print("\nAvailable commands:")
            print("  flask init-db   - Initialize database with default data")
            print("  flask reset-db  - Reset database (WARNING: deletes all data)")
            print("  flask backup-db - Create database backup")
            exit(1)

    # Get configuration from environment
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", 5001))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() == "true"

    print("🚀 Starting Solution Evaluation System...")
    print(f"   Server: http://{host}:{port}")
    print(f"   Debug mode: {debug}")
    print(f"   Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(
        "\n   API Documentation will be available at: http://{host}:{port}/api/health"
    )
    print("   Press Ctrl+C to stop the server\n")

    # Start the development server
    app.run(host=host, port=port, debug=debug)

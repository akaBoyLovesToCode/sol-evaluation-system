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

        # Create default admin user if it doesn't exist
        from app.models import User

        admin_user = User.query.filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@evaluation.local",
                password="admin123",  # Change this in production!
                full_name="System Administrator",
                role="admin",
                department="IT",
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✓ Default admin user created (username: admin, password: admin123)")
            print("  ⚠️  Please change the default password after first login!")
        else:
            print("✓ Admin user already exists")

        print("\n🎉 Database initialization completed successfully!")
        print("\nNext steps:")
        print("1. Start the application: python run.py")
        print("2. Login with admin credentials and change the password")
        print("3. Create additional users as needed")

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


@app.cli.command()
@with_appcontext
def create_user():
    """Create a new user interactively"""
    try:
        from app.models import User

        print("Create New User")
        print("-" * 20)

        username = click.prompt("Username")
        email = click.prompt("Email")
        password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
        full_name = click.prompt("Full Name")
        role = click.prompt(
            "Role",
            type=click.Choice(["admin", "group_leader", "part_leader", "user"]),
            default="user",
        )
        department = click.prompt("Department", default="")

        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            print(
                f"❌ User with username '{username}' or email '{email}' already exists"
            )
            return 1

        # Create new user
        user = User(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role=role,
            department=department if department else None,
        )

        db.session.add(user)
        db.session.commit()

        print(f"✓ User '{username}' created successfully with role '{role}'")

    except Exception as e:
        print(f"❌ User creation failed: {str(e)}")
        db.session.rollback()
        return 1


@app.cli.command()
@with_appcontext
def list_users():
    """List all users in the system"""
    try:
        from app.models import User

        users = User.query.all()

        if not users:
            print("No users found in the system")
            return

        print(
            f"{'ID':<4} {'Username':<15} {'Email':<25} {'Full Name':<20} {'Role':<15} {'Active':<8}"
        )
        print("-" * 90)

        for user in users:
            print(
                f"{user.id:<4} {user.username:<15} {user.email:<25} {user.full_name:<20} {user.role:<15} {'Yes' if user.is_active else 'No':<8}"
            )

        print(f"\nTotal users: {len(users)}")

    except Exception as e:
        print(f"❌ Failed to list users: {str(e)}")
        return 1


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
            print("  flask init-db     - Initialize database with default data")
            print("  flask reset-db    - Reset database (WARNING: deletes all data)")
            print("  flask create-user - Create a new user")
            print("  flask list-users  - List all users")
            print("  flask backup-db   - Create database backup")
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

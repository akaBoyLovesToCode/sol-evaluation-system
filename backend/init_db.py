#!/usr/bin/env python3
"""Database initialization script for PostgreSQL setup.

This script helps initialize a new PostgreSQL database with the required
schema and optional seed data for the Solution Evaluation System.
"""

import sys

from flask_migrate import upgrade
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.user import User


def init_database():
    """Initialize database with schema and seed data."""
    print("🚀 Initializing database...")

    # Create Flask app
    app = create_app("production")

    with app.app_context():
        try:
            # Print database URI for debugging (without password)
            db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
            safe_uri = db_uri.split("@")[1] if "@" in db_uri else db_uri
            print(f"📊 Database: {safe_uri}")

            # Run migrations to create schema
            print("📋 Running database migrations...")
            upgrade()
            print("✅ Migrations completed successfully")

            # Check if admin user exists
            admin_user = User.query.filter_by(username="admin").first()
            if not admin_user:
                print("👤 Creating default admin user...")
                admin_user = User(
                    username="admin",
                    email="admin@evaluation.system",
                    password="admin123",
                    full_name="System Administrator",
                    role="admin",
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Admin user created (username: admin, password: admin123)")
            else:
                print("👤 Admin user already exists. Resetting password...")
                admin_user.set_password("admin123")
                db.session.commit()
                print("✅ Admin password has been reset to 'admin123'")

            print("🎉 Database initialization completed successfully!")

        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    init_database()

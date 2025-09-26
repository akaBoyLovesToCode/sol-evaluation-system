"""Pytest configuration file for the backend tests."""

import os

import pytest

from app import create_app
from app.models import db as _db


@pytest.fixture(scope="session")
def app():
    """Create and configure a Flask app for testing."""
    # Set the testing configuration
    os.environ["FLASK_ENV"] = "testing"
    os.environ["TESTING"] = "True"

    # Create the app with the testing configuration
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "JWT_SECRET_KEY": "test-secret-key",
            "PRESERVE_CONTEXT_ON_EXCEPTION": False,
        }
    )

    # Create the application context
    with app.app_context():
        yield app


@pytest.fixture(scope="session")
def db(app):
    """Create and configure a database for testing."""
    # Create the database and tables
    _db.create_all()

    yield _db

    # Teardown - drop all tables
    _db.session.remove()
    _db.drop_all()


@pytest.fixture(scope="function")
def session(db):
    """Create a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    # Configure the existing session to use our connection
    original_bind = db.session.bind
    db.session.configure(bind=connection)

    yield db.session

    # Cleanup - remove all data and rollback
    db.session.remove()
    transaction.rollback()
    connection.close()

    # Restore the original bind
    db.session.configure(bind=original_bind)


@pytest.fixture(scope="function")
def client(app):
    """Create a test client for the app."""
    return app.test_client()

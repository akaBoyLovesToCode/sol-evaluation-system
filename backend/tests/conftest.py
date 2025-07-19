"""
Pytest configuration file for the backend tests.
"""
import os
import pytest
from app import create_app
from app.models import db as _db
from flask_jwt_extended import create_access_token
from app.models.user import User, UserRole

@pytest.fixture(scope='session')
def app():
    """Create and configure a Flask app for testing."""
    # Set the testing configuration
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'True'
    
    # Create the app with the testing configuration
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret-key',
        'PRESERVE_CONTEXT_ON_EXCEPTION': False
    })
    
    # Create the application context
    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def db(app):
    """Create and configure a database for testing."""
    # Create the database and tables
    _db.create_all()
    
    yield _db
    
    # Teardown - drop all tables
    _db.session.remove()
    _db.drop_all()


@pytest.fixture(scope='function')
def session(db):
    """Create a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # Create a session bound to the connection
    session = db.create_scoped_session(
        options=dict(bind=connection, binds={})
    )
    
    # Set the session for the db
    db.session = session
    
    yield session
    
    # Rollback the transaction
    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def admin_user(session):
    """Create an admin user for testing."""
    user = User(
        username='admin',
        email='admin@example.com',
        full_name='Admin User',
        role=UserRole.ADMIN.value
    )
    user.set_password('Password123')
    session.add(user)
    session.commit()
    return user


@pytest.fixture(scope='function')
def regular_user(session):
    """Create a regular user for testing."""
    user = User(
        username='user',
        email='user@example.com',
        full_name='Regular User',
        role=UserRole.USER.value
    )
    user.set_password('Password123')
    session.add(user)
    session.commit()
    return user


@pytest.fixture(scope='function')
def admin_token(admin_user):
    """Create a JWT token for the admin user."""
    return create_access_token(identity=admin_user.id)


@pytest.fixture(scope='function')
def user_token(regular_user):
    """Create a JWT token for the regular user."""
    return create_access_token(identity=regular_user.id)


@pytest.fixture(scope='function')
def admin_headers(admin_token):
    """Create headers with admin JWT token."""
    return {'Authorization': f'Bearer {admin_token}'}


@pytest.fixture(scope='function')
def user_headers(user_token):
    """Create headers with user JWT token."""
    return {'Authorization': f'Bearer {user_token}'}
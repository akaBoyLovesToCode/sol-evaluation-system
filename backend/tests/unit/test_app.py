"""
Basic tests for the Flask application.
"""
import pytest
from flask import Flask


def test_app_creation(app):
    """Test that the app is created correctly."""
    assert isinstance(app, Flask)
    assert app.config['TESTING'] is True


def test_client_creation(client):
    """Test that the test client is created correctly."""
    response = client.get('/')
    assert response.status_code in (200, 404)  # Either OK or Not Found is acceptable for the root route


def test_admin_user_creation(admin_user):
    """Test that the admin user is created correctly."""
    assert admin_user.username == 'admin'
    assert admin_user.email == 'admin@example.com'
    assert admin_user.role == 'admin'
    assert admin_user.check_password('Password123') is True


def test_regular_user_creation(regular_user):
    """Test that the regular user is created correctly."""
    assert regular_user.username == 'user'
    assert regular_user.email == 'user@example.com'
    assert regular_user.role == 'user'
    assert regular_user.check_password('Password123') is True
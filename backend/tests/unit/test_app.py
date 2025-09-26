"""Basic tests for the Flask application."""

from flask import Flask


def test_app_creation(app):
    """Test that the app is created correctly."""
    assert isinstance(app, Flask)
    assert app.config["TESTING"] is True


def test_client_creation(client):
    """Test that the test client is created correctly."""
    response = client.get("/")
    assert response.status_code in (
        200,
        404,
    )  # Either OK or Not Found is acceptable for the root route

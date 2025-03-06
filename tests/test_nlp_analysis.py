import pytest
import json
from flask import url_for
from flask_login import login_user
from unittest.mock import patch
from models import User  # Import User model from your app
import requests

@pytest.fixture
def test_client():
    from app import app  # Import your Flask app
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    # Set SERVER_NAME so that cookie handling works reliably
    app.config["SERVER_NAME"] = "localhost"
    print("SECRET_KEY:", app.config['SECRET_KEY'])
    print("Initializing test client")
    client = app.test_client()
    return client

@pytest.fixture
def logged_in_user(test_client):
    from app import app
    with app.app_context():
        # Create a mock user
        user = User(id=1, username="testuser")
        # Use the test client as a context manager to establish a request context
        with test_client as client:
            # Trigger a simple GET request to establish context
            client.get("/")
            # Manually set session data to simulate a logged-in user
            with client.session_transaction() as session:
                session["_user_id"] = str(user.id)
                session["_fresh"] = True  # Optional: mark session as fresh
            # Debug: attempt to print cookies if available
            try:
                print("Cookies after login simulation:", client.cookie_jar)
            except AttributeError:
                print("Client does not support cookie_jar attribute.")
        return user

@patch("requests.get")  # Mock article fetching
@patch("requests.post")  # Mock Hugging Face API request
def test_sentiment_analysis_success(mock_post, mock_get, test_client, logged_in_user):
    print("Running test_sentiment_analysis_success")
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "This is a test article. It is positive!"
    
    # Provide the expected mock JSON response; note that only one assignment is needed.
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = [
        [{"label": "NEGATIVE", "score": 0.05}, {"label": "POSITIVE", "score": 0.95}]
    ]
    
    # POST to the main endpoint; follow redirects to capture final response
    response = test_client.post("/", data={"url": "http://example.com"}, follow_redirects=True)
    
    assert response.status_code == 200
    print("Response data:", response.data)
    data = json.loads(response.data)
    assert "positive_score" in data
    assert data["positive_score"] == 0.95

@patch("requests.get")
def test_sentiment_analysis_invalid_url(mock_get, test_client, logged_in_user):
    print("Running test_sentiment_analysis_invalid_url")
    mock_get.side_effect = requests.RequestException("Failed to fetch article")
    
    response = test_client.post("/", data={"url": "http://invalid-url.com"})
    
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data
    assert "Failed to fetch the article" in data["error"]

@patch("requests.post")
def test_sentiment_analysis_huggingface_failure(mock_post, test_client, logged_in_user):
    print("Running test_sentiment_analysis_huggingface_failure")
    mock_post.return_value.status_code = 500
    
    response = test_client.post("/", data={"url": "http://example.com"})
    
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data
    assert "Failed to contact Hugging Face API" in data["error"]

def test_sentiment_analysis_unauthenticated(test_client):
    print("Running test_sentiment_analysis_unauthenticated")
    # This test does not simulate login; it should redirect to the login page.
    response = test_client.post("/", data={"url": "http://example.com"}, follow_redirects=True)
    
    assert response.status_code == 200  # After following redirects, we expect the login page
    assert b"Login" in response.data  # Check that the login page is displayed

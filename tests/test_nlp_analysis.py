import pytest
import json
from flask_login import login_user
from unittest.mock import patch
from models import User  # Import your User model
import requests

@pytest.fixture
def test_client():
    """
    Create a Flask test client for making HTTP requests to the app.
    """
    from app import app  # Import the Flask app instance
    # Set up testing configuration
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    # Setting SERVER_NAME helps with cookie/session handling
    app.config["SERVER_NAME"] = "localhost"
    
    # Debug prints to verify configuration
    print("SECRET_KEY:", app.config['SECRET_KEY'])
    print("Initializing test client")
    
    client = app.test_client()
    return client

@pytest.fixture
def signed_up_and_logged_in_client(test_client):
    """
    Use the /signup and /login endpoints to create a user and log them in.
    
    This fixture:
      1. Sends a POST request to the /signup endpoint with user data.
      2. Sends a POST request to the /login endpoint with the same credentials.
      3. Returns the test client, which should now be logged in.
    """
    # Data for signing up a new user
    signup_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    # Use follow_redirects=True so that the entire signup flow is executed
    response_signup = test_client.post("/signup", data=signup_data, follow_redirects=True)
    # Optionally, you can print or assert parts of the response to ensure signup succeeded.
    print("Signup response status code:", response_signup.status_code)
    
    # Data for logging in with the new user
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    # Log in via the /login endpoint, following redirects so that the session is set
    response_login = test_client.post("/login", data=login_data, follow_redirects=True)
    print("Login response status code:", response_login.status_code)
    
    # At this point, the test client should have the session cookie for the logged-in user.
    return test_client

@patch("requests.get")  # Mock article fetching
@patch("requests.post")  # Mock Hugging Face API request
def test_sentiment_analysis_success(mock_post, mock_get, signed_up_and_logged_in_client):
    """
    Test the sentiment analysis endpoint for a successful response.
    """
    print("Running test_sentiment_analysis_success")
    
    # Configure mocks for external calls
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "This is a test article. It is positive!"
    
    mock_post.return_value.status_code = 200
    # Provide a mock JSON response from the Hugging Face API
    mock_post.return_value.json.return_value = [
        [{"label": "NEGATIVE", "score": 0.05}, {"label": "POSITIVE", "score": 0.95}]
    ]
    
    # POST to the main endpoint using the logged-in client;
    # follow_redirects=True ensures we get the final response after any redirects.
    response = signed_up_and_logged_in_client.post("/", data={"url": "http://example.com"}, follow_redirects=True)
    
    # We expect a 200 OK response if the user is authenticated and processing succeeds.
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    print("Response data:", response.data)
    
    # Convert the response data (JSON) into a Python dictionary
    data = json.loads(response.data)
    # Check that the response contains the expected key and value.
    assert "positive_score" in data
    assert data["positive_score"] == 0.95

@patch("requests.get")
def test_sentiment_analysis_invalid_url(mock_get, signed_up_and_logged_in_client):
    """
    Test the endpoint for handling an invalid URL, expecting an error response.
    """
    print("Running test_sentiment_analysis_invalid_url")
    # Simulate a request failure (e.g., URL not reachable)
    mock_get.side_effect = requests.RequestException("Failed to fetch article")
    
    response = signed_up_and_logged_in_client.post("/", data={"url": "http://invalid-url.com"})
    
    # The app should return a 500 error for a failed fetch
    assert response.status_code == 500, f"Expected 500, got {response.status_code}"
    data = json.loads(response.data)
    assert "error" in data
    assert "Failed to fetch the article" in data["error"]

@patch("requests.post")
def test_sentiment_analysis_huggingface_failure(mock_post, signed_up_and_logged_in_client):
    """
    Test the endpoint for handling a failure from the Hugging Face API.
    """
    print("Running test_sentiment_analysis_huggingface_failure")
    # Simulate a failure response from the API
    mock_post.return_value.status_code = 500
    
    response = signed_up_and_logged_in_client.post("/", data={"url": "http://example.com"})
    
    # The app should return a 500 error for API failures
    assert response.status_code == 500, f"Expected 500, got {response.status_code}"
    data = json.loads(response.data)
    assert "error" in data
    assert "Failed to contact Hugging Face API" in data["error"]

def test_sentiment_analysis_unauthenticated(test_client):
    """
    Test that when the user is not logged in, the protected route redirects to the login page.
    """
    print("Running test_sentiment_analysis_unauthenticated")
    # Without simulating login, the endpoint should redirect to the login page.
    response = test_client.post("/", data={"url": "http://example.com"}, follow_redirects=True)
    
    # After following redirects, the response should be the login page (status 200)
    assert response.status_code == 200
    # Check that the response contains text indicating a login page (e.g., "Login")
    assert b"Login" in response.data

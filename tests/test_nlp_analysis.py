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
    client = app.test_client()
    return client

@pytest.fixture
def logged_in_user(test_client):
    from app import app
    with app.app_context():  # Ensure the application context is active
        user = User(id=1, username="testuser")  # Create a mock user
        
        with test_client:  # Ensure test_client has a request context
            test_client.get("/")  # Create an active request context
            login_user(user)  # Now Flask-Login has a request context
            
            with test_client.session_transaction() as session:
                session["_user_id"] = str(user.id)  # Mock session login
            
        return user


@patch("requests.get")  # Mock article fetching
@patch("requests.post")  # Mock Hugging Face API request
def test_sentiment_analysis_success(mock_post, mock_get, test_client, logged_in_user):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "This is a test article. It is positive!"
    
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = [{
        "label": "POSITIVE", "score": 0.95
    }]
    mock_post.return_value.json.return_value = [[{"label":"NEGATIVE","score":0.05},{"label":"POSITIVE","score":0.95}]]
    response = test_client.post("/", data={"url": "http://example.com"}, follow_redirects=True)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "positive_score" in data
    assert data["positive_score"] == 0.95

@patch("requests.get")
def test_sentiment_analysis_invalid_url(mock_get, test_client, logged_in_user):
    mock_get.side_effect = requests.RequestException("Failed to fetch article")
    
    response = test_client.post("/", data={"url": "http://invalid-url.com"})
    
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data
    assert "Failed to fetch the article" in data["error"]

@patch("requests.post")
def test_sentiment_analysis_huggingface_failure(mock_post, test_client, logged_in_user):
    mock_post.return_value.status_code = 500
    
    response = test_client.post("/", data={"url": "http://example.com"})
    
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data
    assert "Failed to contact Hugging Face API" in data["error"]


def test_sentiment_analysis_unauthenticated(test_client):
    response = test_client.post("/", data={"url": "http://example.com"}, follow_redirects=True)
    
    assert response.status_code == 200  # Redirects to login
    assert b"Login" in response.data  # Ensure login page is shown

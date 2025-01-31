import pytest
from app import app
from unittest.mock import patch


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_index(client,mocker):
    """Test the home page (GET request)."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Enter Article URL" in response.data

def test_post_missing_url(client):
    """Test POST request with missing URL."""
    response = client.post('/')
    assert response.status_code == 400
    assert response.json == {"error": "URL is required"}

def test_post_api_failure(client, mocker):
    """Test POST request when MeaningCloud API fails."""
    # Mock the requests.post call
    mock_response = mocker.Mock()
    mock_response.status_code = 500

    mocker.patch('requests.post', return_value=mock_response)

    response = client.post('/', data={'url': 'https://example.com/article'})
    assert response.status_code == 500
    assert response.json == {"error": "Failed to contact MeaningCloud API"}

def test_post_valid_response(client, mocker):
    """Test POST request with a valid response from MeaningCloud API."""
    # Mock the requests.post call
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "score_tag": "P+",
        "agreement": "AGREEMENT",
        "subjectivity": "OBJECTIVE",
        "confidence": "100",
        "irony": "NONIRONIC"
    }
    mock_response.status_code = 200  # Ensure the mock response has a valid status_code

    mocker.patch('requests.post', return_value=mock_response)

    response = client.post('/', data={'url': 'https://example.com/article'})

    assert response.status_code == 200
    assert response.json == {
        "score_tag": "P+",
        "agreement": "AGREEMENT",
        "subjectivity": "OBJECTIVE",
        "confidence": "100",
        "irony": "NONIRONIC"
    }

def test_post_partial_response(client,mocker):
    """Test POST request with a partial response from MeaningCloud API."""
    # Mock a partial API response
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "agreement": "DISAGREEMENT",
        "confidence": "80"
    }
    mocker.patch('requests.post', return_value=mock_response)

    response = client.post('/', data={'url': 'https://example.com/article'})
    assert response.status_code == 200
    assert response.json == {
        "score_tag": "NONE",  # Default value
        "agreement": "DISAGREEMENT",
        "subjectivity": "UNKNOWN",  # Default value
        "confidence": "80",
        "irony": "UNKNOWN"  # Default value
    }

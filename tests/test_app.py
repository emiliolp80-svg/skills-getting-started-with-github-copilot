import pytest
from fastapi.testclient import TestClient
import src.app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test."""
    app_module.activities = {
        "Test Activity": {
            "description": "A test activity for testing purposes",
            "schedule": "Mondays, 10:00 AM",
            "max_participants": 2,
            "participants": []
        }
    }


@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    return TestClient(app_module.app)


def test_get_activities(client):
    """Test GET /activities returns the activities dictionary."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Test Activity" in data
    assert data["Test Activity"]["description"] == "A test activity for testing purposes"
    assert data["Test Activity"]["participants"] == []


def test_signup_success(client):
    """Test successful signup for an activity."""
    response = client.post("/activities/Test%20Activity/signup?email=test@example.com")
    assert response.status_code == 200
    result = response.json()
    assert "Signed up test@example.com for Test Activity" == result["message"]

    # Verify participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Test Activity"]["participants"]


def test_signup_activity_not_found(client):
    """Test signup for a non-existent activity."""
    response = client.post("/activities/NonExistent/signup?email=test@example.com")
    assert response.status_code == 404
    result = response.json()
    assert result["detail"] == "Activity not found"


def test_signup_already_signed_up(client):
    """Test signup when student is already signed up."""
    # First signup
    client.post("/activities/Test%20Activity/signup?email=test@example.com")
    # Second signup
    response = client.post("/activities/Test%20Activity/signup?email=test@example.com")
    assert response.status_code == 400
    result = response.json()
    assert result["detail"] == "Student already signed up for this activity"


def test_unregister_success(client):
    """Test successful unregister from an activity."""
    # First signup
    client.post("/activities/Test%20Activity/signup?email=test@example.com")
    # Then unregister
    response = client.delete("/activities/Test%20Activity/unregister?email=test@example.com")
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered test@example.com from Test Activity" == result["message"]

    # Verify participant was removed
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" not in data["Test Activity"]["participants"]


def test_unregister_activity_not_found(client):
    """Test unregister from a non-existent activity."""
    response = client.delete("/activities/NonExistent/unregister?email=test@example.com")
    assert response.status_code == 404
    result = response.json()
    assert result["detail"] == "Activity not found"


def test_unregister_not_signed_up(client):
    """Test unregister when student is not signed up."""
    response = client.delete("/activities/Test%20Activity/unregister?email=test@example.com")
    assert response.status_code == 404
    result = response.json()
    assert result["detail"] == "Student not signed up for this activity"
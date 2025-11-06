import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Check activity structure
    for name, details in activities.items():
        assert isinstance(name, str)
        assert isinstance(details, dict)
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)

def test_signup_for_activity():
    """Test signing up for an activity"""
    # Get available activities
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    
    # Test successful signup
    email = "test@example.com"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]
    
    # Test duplicate signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # First sign up a participant
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    email = "unregister_test@example.com"
    
    # Sign up
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Test successful unregistration
    response = client.post(
        f"/activities/{activity_name}/unregister",
        json={"email": email}
    )
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]
    
    # Test unregistering non-existent participant
    response = client.post(
        f"/activities/{activity_name}/unregister",
        json={"email": "nonexistent@example.com"}
    )
    assert response.status_code == 400
    assert "not found in this activity" in response.json()["detail"]

def test_invalid_activity():
    """Test operations with non-existent activity"""
    activity_name = "non_existent_activity"
    email = "test@example.com"
    
    # Test signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
    
    # Test unregister
    response = client.post(
        f"/activities/{activity_name}/unregister",
        json={"email": email}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

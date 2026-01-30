"""Tests for the Mergington High School API"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities before each test"""
    # Store original activities
    original_activities = {
        "Debate Club": {
            "description": "Develop public speaking and argumentation skills through competitive debate",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore scientific concepts through experiments and demonstrations",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 25,
            "participants": ["james@mergington.edu", "lucy@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["marcus@mergington.edu"]
        },
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for getting activities"""
    
    def test_get_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Debate Club" in data
        assert "Science Club" in data
        assert "Basketball Team" in data
        assert data["Debate Club"]["description"] == "Develop public speaking and argumentation skills through competitive debate"
    
    def test_get_activities_has_participants(self, client):
        """Test that activities include participant lists"""
        response = client.get("/activities")
        data = response.json()
        assert "participants" in data["Debate Club"]
        assert "alex@mergington.edu" in data["Debate Club"]["participants"]


class TestSignup:
    """Tests for signing up for activities"""
    
    def test_signup_success(self, client):
        """Test successful signup"""
        response = client.post(
            "/activities/Debate%20Club/signup?email=newemail@mergington.edu",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newemail@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        updated_activities = activities_response.json()
        assert "newemail@mergington.edu" in updated_activities["Debate Club"]["participants"]
    
    def test_signup_duplicate_email(self, client):
        """Test signup with already registered email"""
        response = client.post(
            "/activities/Debate%20Club/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Fake%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestUnregister:
    """Tests for unregistering from activities"""
    
    def test_unregister_success(self, client):
        """Test successful unregister"""
        response = client.post(
            "/activities/Debate%20Club/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "alex@mergington.edu" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        updated_activities = activities_response.json()
        assert "alex@mergington.edu" not in updated_activities["Debate Club"]["participants"]
    
    def test_unregister_not_signed_up(self, client):
        """Test unregister for participant not signed up"""
        response = client.post(
            "/activities/Debate%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity"""
        response = client.post(
            "/activities/Fake%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestRoot:
    """Tests for root endpoint"""
    
    def test_root_redirect(self, client):
        """Test root endpoint redirects to static html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]

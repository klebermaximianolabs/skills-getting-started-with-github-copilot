"""
Tests for POST /activities/{activity_name}/signup endpoint.

Tests student signup functionality including happy paths, error cases,
and state persistence.
"""

import pytest


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client):
        """Test successful signup for a new student."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant to the activity."""
        email = "testuser@mergington.edu"
        
        # Sign up
        client.post("/activities/Programming Class/signup", params={"email": email})
        
        # Verify in activities list
        activities = client.get("/activities").json()
        participants = activities["Programming Class"]["participants"]
        assert email in participants

    def test_signup_multiple_students_different_activities(self, client):
        """Test multiple students can sign up for different activities."""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        client.post("/activities/Tennis Club/signup", params={"email": email1})
        client.post("/activities/Art Studio/signup", params={"email": email2})

        activities = client.get("/activities").json()
        assert email1 in activities["Tennis Club"]["participants"]
        assert email2 in activities["Art Studio"]["participants"]

    def test_signup_already_signed_up_returns_400(self, client):
        """Test that signing up twice returns 400 error."""
        email = "duplicatestudent@mergington.edu"
        activity = "Science Club"

        # First signup succeeds
        response1 = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response1.status_code == 200

        # Second signup fails
        response2 = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_existing_participant_returns_400(self, client):
        """Test that signup fails for student already in the activity."""
        # michael@mergington.edu is already in Chess Club (from fresh_activities)
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_activity_not_found_returns_404(self, client):
        """Test that signup to non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_various_activities(self, client):
        """Test signup works for different activities."""
        activities_to_test = ["Chess Club", "Drama Club", "Science Club", "Basketball Team"]
        
        for i, activity in enumerate(activities_to_test):
            email = f"student{i}@mergington.edu"
            response = client.post(f"/activities/{activity}/signup", params={"email": email})
            assert response.status_code == 200

    @pytest.mark.parametrize("activity", [
        "Chess Club",
        "Programming Class",
        "Basketball Team"
    ])
    def test_signup_parametrized(self, client, activity):
        """Test signup works for different activities using parametrization."""
        email = f"test_{activity.replace(' ', '_')}@mergington.edu"
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response.status_code == 200

    def test_signup_persists_across_requests(self, client):
        """Test that signup changes persist across multiple requests."""
        email = "persistentuser@mergington.edu"
        activity = "Debate Team"

        # Sign up
        client.post(f"/activities/{activity}/signup", params={"email": email})

        # Check multiple times - data should persist
        for _ in range(3):
            activities = client.get("/activities").json()
            assert email in activities[activity]["participants"]

    def test_signup_increments_participant_count(self, client):
        """Test that signup increments the participant count."""
        activity = "Tennis Club"
        email = "newtennis@mergington.edu"

        # Get initial count
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities[activity]["participants"])

        # Sign up
        client.post(f"/activities/{activity}/signup", params={"email": email})

        # Get new count
        updated_activities = client.get("/activities").json()
        updated_count = len(updated_activities[activity]["participants"])

        assert updated_count == initial_count + 1

    def test_signup_email_case_sensitivity(self, client):
        """Test signup with different email cases."""
        email_lower = "casesensitive@mergington.edu"
        email_upper = "CASESENSITIVE@mergington.edu"

        response1 = client.post("/activities/Art Studio/signup", params={"email": email_lower})
        assert response1.status_code == 200

        # Email is case-sensitive in signup
        response2 = client.post("/activities/Art Studio/signup", params={"email": email_upper})
        assert response2.status_code == 200  # Should succeed because it's a different string

    def test_signup_whitespace_in_email(self, client):
        """Test signup with email containing special characters."""
        email = "student.name+tag@mergington.edu"
        response = client.post(
            "/activities/Drama Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200

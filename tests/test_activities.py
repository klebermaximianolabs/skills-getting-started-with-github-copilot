"""
Tests for GET /activities endpoint.

Tests the retrieval of all available activities and validates the response structure.
"""

from fastapi.testclient import TestClient


class TestGetActivities:
    """Test suite for GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns a 200 status code."""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities in the database."""
        response = client.get("/activities")
        data = response.json()

        # Should have 9 activities
        assert len(data) == 9

        # Verify some expected activities are present
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Drama Club" in data

    def test_activities_have_correct_structure(self, client):
        """Test that each activity has the required fields."""
        response = client.get("/activities")
        activities = response.json()

        # Check each activity has required fields
        required_fields = {"description", "schedule", "max_participants", "participants"}
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict), f"{activity_name} should be a dict"
            assert required_fields.issubset(
                activity_data.keys()
            ), f"{activity_name} missing required fields"

    def test_activity_data_types(self, client):
        """Test that activity data has correct types."""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            assert all(isinstance(p, str) for p in activity_data["participants"])

    def test_chess_club_data(self, client):
        """Test that Chess Club activity data is correct."""
        response = client.get("/activities")
        activities = response.json()

        chess_club = activities["Chess Club"]
        assert "Learn strategies" in chess_club["description"]
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]
        assert len(chess_club["participants"]) == 2

    def test_activity_participants_are_valid_emails(self, client):
        """Test that all participants have valid email formats."""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
            for email in activity_data["participants"]:
                # Basic email validation
                assert "@" in email, f"Invalid email in {activity_name}: {email}"
                assert "." in email.split("@")[1], f"Invalid email in {activity_name}: {email}"

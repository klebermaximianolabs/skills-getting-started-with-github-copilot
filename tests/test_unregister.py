"""
Tests for POST /activities/{activity_name}/unregister endpoint.

Tests student unregister functionality including happy paths, error cases,
and state persistence.
"""

import pytest


class TestUnregisterFromActivity:
    """Test suite for POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successful(self, client):
        """Test successful unregister for a registered student."""
        # michael@mergington.edu is in Chess Club by default
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant."""
        email = "michael@mergington.edu"
        
        # Unregister
        client.post("/activities/Chess Club/unregister", params={"email": email})
        
        # Verify removed from activities list
        activities = client.get("/activities").json()
        participants = activities["Chess Club"]["participants"]
        assert email not in participants

    def test_unregister_multiple_participants(self, client):
        """Test unregistering multiple different participants."""
        # Both michael and daniel are in Chess Club
        client.post("/activities/Chess Club/unregister", params={"email": "michael@mergington.edu"})
        client.post("/activities/Chess Club/unregister", params={"email": "daniel@mergington.edu"})

        activities = client.get("/activities").json()
        participants = activities["Chess Club"]["participants"]
        assert "michael@mergington.edu" not in participants
        assert "daniel@mergington.edu" not in participants
        assert len(participants) == 0

    def test_unregister_not_registered_returns_400(self, client):
        """Test that unregistering a non-participant returns 400."""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()

    def test_unregister_already_unregistered_returns_400(self, client):
        """Test unregistering a student twice returns 400 on second attempt."""
        email = "michael@mergington.edu"

        # First unregister succeeds
        response1 = client.post("/activities/Chess Club/unregister", params={"email": email})
        assert response1.status_code == 200

        # Second unregister fails
        response2 = client.post("/activities/Chess Club/unregister", params={"email": email})
        assert response2.status_code == 400
        data = response2.json()
        assert "not registered" in data["detail"].lower()

    def test_unregister_activity_not_found_returns_404(self, client):
        """Test that unregister from non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_from_various_activities(self, client):
        """Test unregister works for different activities with preexisting participants."""
        # These activities come with default participants
        test_cases = [
            ("Chess Club", "michael@mergington.edu"),
            ("Programming Class", "emma@mergington.edu"),
            ("Drama Club", "marcus@mergington.edu"),
        ]

        for activity, email in test_cases:
            response = client.post(
                f"/activities/{activity}/unregister",
                params={"email": email}
            )
            assert response.status_code == 200

    @pytest.mark.parametrize("activity,email", [
        ("Chess Club", "michael@mergington.edu"),
        ("Programming Class", "sophia@mergington.edu"),
        ("Debate Team", "rachel@mergington.edu"),
    ])
    def test_unregister_parametrized(self, client, activity, email):
        """Test unregister for different activities using parametrization."""
        response = client.post(f"/activities/{activity}/unregister", params={"email": email})
        assert response.status_code == 200

    def test_unregister_persists_across_requests(self, client):
        """Test that unregister changes persist across multiple requests."""
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Unregister
        client.post(f"/activities/{activity}/unregister", params={"email": email})

        # Check multiple times - data should persist
        for _ in range(3):
            activities = client.get("/activities").json()
            assert email not in activities[activity]["participants"]

    def test_unregister_decrements_participant_count(self, client):
        """Test that unregister decrements the participant count."""
        activity = "Chess Club"
        email = "michael@mergington.edu"

        # Get initial count
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities[activity]["participants"])

        # Unregister
        client.post(f"/activities/{activity}/unregister", params={"email": email})

        # Get new count
        updated_activities = client.get("/activities").json()
        updated_count = len(updated_activities[activity]["participants"])

        assert updated_count == initial_count - 1

    def test_signup_after_unregister(self, client):
        """Test that a student can re-signup after unregistering."""
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Unregister
        client.post(f"/activities/{activity}/unregister", params={"email": email})

        # Sign up again
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response.status_code == 200

        # Verify in participants
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]

    def test_unregister_one_does_not_affect_others(self, client):
        """Test that unregistering one participant doesn't affect others."""
        activity = "Chess Club"

        # Get other participants before
        activities_before = client.get("/activities").json()
        participants_before = set(activities_before[activity]["participants"])

        # Unregister one
        email_to_remove = "michael@mergington.edu"
        client.post(f"/activities/{activity}/unregister", params={"email": email_to_remove})

        # Get participants after
        activities_after = client.get("/activities").json()
        participants_after = set(activities_after[activity]["participants"])

        # Verify only that one was removed
        assert (participants_before - {email_to_remove}) == participants_after

    def test_unregister_email_case_sensitivity(self, client):
        """Test unregister with different email cases."""
        # First sign up both variants
        email_lower = "casesensitive@mergington.edu"
        email_upper = "CASESENSITIVE@mergington.edu"

        client.post("/activities/Art Studio/signup", params={"email": email_lower})
        client.post("/activities/Art Studio/signup", params={"email": email_upper})

        # Unregister lowercase
        response = client.post("/activities/Art Studio/unregister", params={"email": email_lower})
        assert response.status_code == 200

        # Verify lowercase is removed but uppercase remains
        activities = client.get("/activities").json()
        participants = activities["Art Studio"]["participants"]
        assert email_lower not in participants
        assert email_upper in participants

    def test_unregister_from_full_activity(self, client):
        """Test unregister from an activity that's at max capacity."""
        activity = "Gym Class"
        
        # Gym Class has max_participants 30 and 2 current participants
        # Add more to fill it up
        for i in range(28):
            email = f"filler{i}@mergington.edu"
            client.post(f"/activities/{activity}/signup", params={"email": email})

        # Verify it's full (30 participants)
        activities = client.get("/activities").json()
        assert len(activities[activity]["participants"]) == 30

        # Should still be able to unregister
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": "john@mergington.edu"}
        )
        assert response.status_code == 200

        # Verify count decreased
        activities = client.get("/activities").json()
        assert len(activities[activity]["participants"]) == 29

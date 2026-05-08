import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirect_to_static(self, client):
        """Test that root path redirects to static HTML file"""
        # Arrange
        expected_redirect_path = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_path


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities_success(self, client):
        """Test retrieving all activities returns complete list"""
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Science Club"
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert sorted(data.keys()) == sorted(expected_activities)
        assert len(data) == 9

    def test_get_activities_has_correct_structure(self, client):
        """Test that activities response has expected structure"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert isinstance(data, dict)
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(activity_data.keys())
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_participants_are_emails(self, client):
        """Test that participants list contains email addresses"""
        # Arrange
        # (implicit: participants should be email strings)

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity_data in data.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant


class TestActivitySignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_valid_activity_and_email_success(self, client):
        """Test successful signup for valid activity and email"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_nonexistent_activity_fails(self, client):
        """Test signup for non-existent activity returns 404"""
        # Arrange
        activity_name = "NonExistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_duplicate_email_fails(self, client):
        """Test duplicate signup (same email, same activity) returns 400"""
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already signed up for this activity

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()

    def test_signup_same_email_different_activities_succeeds(self, client):
        """Test same email can signup for multiple different activities"""
        # Arrange
        email = "newuser@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"

        # Act
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        data1 = response1.json()
        data2 = response2.json()
        assert email in data1["message"]
        assert email in data2["message"]
        assert activity1 in data1["message"]
        assert activity2 in data2["message"]

    def test_signup_missing_email_parameter_fails(self, client):
        """Test signup without email parameter returns 422"""
        # Arrange
        activity_name = "Tennis Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup"
        )

        # Assert
        assert response.status_code == 422

    def test_signup_case_sensitive_activity_name(self, client):
        """Test that activity names are case-sensitive"""
        # Arrange
        email = "student@mergington.edu"
        wrong_case_activity = "chess club"  # lowercase instead of "Chess Club"

        # Act
        response = client.post(
            f"/activities/{wrong_case_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_signup_multiple_different_emails_same_activity_succeeds(self, client):
        """Test multiple different emails can signup for the same activity"""
        # Arrange
        activity_name = "Art Studio"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200

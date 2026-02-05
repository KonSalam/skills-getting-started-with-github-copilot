import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_list(self, client):
        """Test that GET /activities returns a list of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
    
    def test_get_activities_contains_required_fields(self, client):
        """Test that each activity contains required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, details in activities.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)
    
    def test_get_activities_has_basketball(self, client):
        """Test that Basketball activity exists"""
        response = client.get("/activities")
        activities = response.json()
        
        assert "Basketball" in activities
        assert activities["Basketball"]["max_participants"] == 15


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": "newemail@mergington.edu"}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "newemail@mergington.edu" in result["message"]
        assert "Basketball" in result["message"]
    
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds participant to list"""
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Basketball"]["participants"])
        
        # Sign up new participant
        client.post(
            "/activities/Basketball/signup",
            params={"email": "newperson@mergington.edu"}
        )
        
        # Check updated count
        response = client.get("/activities")
        updated_count = len(response.json()["Basketball"]["participants"])
        
        assert updated_count == initial_count + 1
        assert "newperson@mergington.edu" in response.json()["Basketball"]["participants"]
    
    def test_signup_duplicate_participant(self, client):
        """Test that duplicate signup returns error"""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": "alex@mergington.edu"}
        )
        
        assert response.status_code == 400
        result = response.json()
        assert "already signed up" in result["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for non-existent activity"""
        response = client.post(
            "/activities/NonExistentActivity/signup",
            params={"email": "test@mergington.edu"}
        )
        
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"].lower()
    
    def test_signup_multiple_activities(self, client):
        """Test that same person can signup for multiple activities"""
        email = "multi@mergington.edu"
        
        # Sign up for two activities
        response1 = client.post(
            "/activities/Basketball/signup",
            params={"email": email}
        )
        response2 = client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both signups
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Basketball"]["participants"]
        assert email in activities["Tennis Club"]["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_participant(self, client):
        """Test unregistering a participant"""
        response = client.delete(
            "/activities/Basketball/unregister",
            params={"email": "alex@mergington.edu"}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "alex@mergington.edu" in result["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant"""
        # Verify participant is there
        response = client.get("/activities")
        assert "alex@mergington.edu" in response.json()["Basketball"]["participants"]
        
        # Unregister
        client.delete(
            "/activities/Basketball/unregister",
            params={"email": "alex@mergington.edu"}
        )
        
        # Verify participant is removed
        response = client.get("/activities")
        assert "alex@mergington.edu" not in response.json()["Basketball"]["participants"]
    
    def test_unregister_nonexistent_participant(self, client):
        """Test unregistering participant not in activity"""
        response = client.delete(
            "/activities/Basketball/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        
        assert response.status_code == 400
        result = response.json()
        assert "not registered" in result["detail"].lower()
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from non-existent activity"""
        response = client.delete(
            "/activities/NonExistentActivity/unregister",
            params={"email": "test@mergington.edu"}
        )
        
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"].lower()
    
    def test_unregister_then_signup_again(self, client):
        """Test that participant can signup again after unregistering"""
        email = "reusable@mergington.edu"
        
        # Sign up
        response1 = client.post(
            "/activities/Drama Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            "/activities/Drama Club/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(
            "/activities/Drama Club/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert email in response.json()["Drama Club"]["participants"]

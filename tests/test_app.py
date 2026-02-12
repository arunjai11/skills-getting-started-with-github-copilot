"""Tests for the Mergington High School Activities API"""
import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that get activities returns all available activities"""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert len(data) == 9
    
    def test_activity_has_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)
    
    def test_activities_contain_participants(self, client, reset_activities):
        """Test that activities include their participants"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_success(self, client, reset_activities):
        """Test successfully signing up a new participant"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant_to_list(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity"""
        client.post(
            "/activities/Basketball Team/signup?email=newplayer@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "newplayer@mergington.edu" in data["Basketball Team"]["participants"]
    
    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """Test that signing up an already registered participant fails"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signing up for a non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_multiple_different_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple activities"""
        email = "versatile@mergington.edu"
        
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        response2 = client.post(
            f"/activities/Drama Club/signup?email={email}"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Drama Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_success(self, client, reset_activities):
        """Test successfully unregistering an existing participant"""
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]
    
    def test_unregister_removes_participant_from_list(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregistering a non-existent participant fails"""
        response = client.post(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregistering from a non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that a student can unregister and sign up again"""
        email = "flexible@mergington.edu"
        activity = "Programming Class"
        
        # Sign up
        response1 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response3.status_code == 200


class TestRootEndpoint:
    """Tests for the GET / endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]

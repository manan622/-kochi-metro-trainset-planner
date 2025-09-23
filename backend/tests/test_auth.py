import pytest
from fastapi.testclient import TestClient
from app.services.auth_service import create_dummy_users, get_password_hash
from app.models.models import User, UserRole

class TestAuthentication:
    """Test authentication functionality"""
    
    def test_login_endpoint_exists(self, client: TestClient):
        """Test that login endpoint is accessible"""
        response = client.post("/api/auth/login", json={
            "username": "nonexistent",
            "password": "wrong"
        })
        assert response.status_code in [401, 422]  # Should not be 404
    
    def test_create_dummy_users(self, db_session):
        """Test that dummy users are created correctly"""
        create_dummy_users(db_session)
        
        # Verify all three dummy users exist
        admin = db_session.query(User).filter(User.username == "admin").first()
        inspector = db_session.query(User).filter(User.username == "inspector").first()
        worker = db_session.query(User).filter(User.username == "worker").first()
        
        assert admin is not None
        assert inspector is not None
        assert worker is not None
        
        assert admin.role == UserRole.MANAGEMENT
        assert inspector.role == UserRole.INSPECTION
        assert worker.role == UserRole.WORKER
    
    def test_successful_login(self, client: TestClient, db_session):
        """Test successful login returns JWT token"""
        # Create dummy users first
        create_dummy_users(db_session)
        
        response = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_invalid_login(self, client: TestClient, db_session):
        """Test invalid login returns 401"""
        create_dummy_users(db_session)
        
        response = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with nonexistent user returns 401"""
        response = client.post("/api/auth/login", json={
            "username": "nonexistent",
            "password": "password"
        })
        
        assert response.status_code == 401
    
    def test_get_current_user_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token returns 401"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
    
    def test_get_current_user_with_valid_token(self, client: TestClient, db_session):
        """Test accessing protected endpoint with valid token"""
        # Create dummy users and login
        create_dummy_users(db_session)
        
        login_response = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        
        token = login_response.json()["access_token"]
        
        response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "management"
    
    def test_logout_endpoint(self, client: TestClient):
        """Test logout endpoint is accessible"""
        response = client.post("/api/auth/logout")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

class TestRoleBasedAccess:
    """Test role-based access control"""
    
    def get_token_for_user(self, client: TestClient, db_session, username: str, password: str):
        """Helper method to get JWT token for a user"""
        create_dummy_users(db_session)
        
        response = client.post("/api/auth/login", json={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            return response.json()["access_token"]
        return None
    
    def test_admin_access(self, client: TestClient, db_session):
        """Test admin user can access management functions"""
        token = self.get_token_for_user(client, db_session, "admin", "admin123")
        assert token is not None
        
        # Test accessing user info
        response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "management"
    
    def test_inspector_access(self, client: TestClient, db_session):
        """Test inspector user has correct role"""
        token = self.get_token_for_user(client, db_session, "inspector", "inspect123")
        assert token is not None
        
        response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "inspection"
    
    def test_worker_access(self, client: TestClient, db_session):
        """Test worker user has correct role"""
        token = self.get_token_for_user(client, db_session, "worker", "work123")
        assert token is not None
        
        response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "worker"

class TestPasswordHashing:
    """Test password hashing functionality"""
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original password
        assert hashed != password
        
        # Hash should be a non-empty string
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        
        # Hash should be deterministic but with salt
        hashed2 = get_password_hash(password)
        assert hashed != hashed2  # Different due to salt
    
    def test_password_verification(self):
        """Test password verification works correctly"""
        from app.services.auth_service import verify_password
        
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Correct password should verify
        assert verify_password(password, hashed) is True
        
        # Wrong password should not verify
        assert verify_password("wrongpassword", hashed) is False
        assert verify_password("", hashed) is False
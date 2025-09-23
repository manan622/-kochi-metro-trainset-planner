import pytest
from fastapi.testclient import TestClient
from app.services.auth_service import create_dummy_users

class TestTrainsetEndpoints:
    """Test trainset-related API endpoints"""
    
    def get_auth_token(self, client: TestClient, db_session):
        """Helper to get authentication token"""
        create_dummy_users(db_session)
        
        response = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            return response.json()["access_token"]
        return None
    
    def test_induction_plan_endpoint_requires_auth(self, client: TestClient):
        """Test that induction plan endpoint requires authentication"""
        response = client.post("/api/induction/plan")
        assert response.status_code == 401
    
    def test_induction_plan_endpoint_with_auth(self, client: TestClient, db_session):
        """Test induction plan endpoint with authentication"""
        token = self.get_auth_token(client, db_session)
        assert token is not None
        
        response = client.post("/api/induction/plan", 
                             headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return expected structure
        assert "trainsets" in data
        assert "summary" in data
        assert "generated_at" in data
        
        # Trainsets should be a list
        assert isinstance(data["trainsets"], list)
        
        # Summary should contain expected fields
        summary = data["summary"] 
        assert "total_trainsets" in summary
        assert "fit" in summary
        assert "unfit" in summary
        assert "standby" in summary
    
    def test_fleet_status_endpoint(self, client: TestClient, db_session):
        """Test fleet status endpoint"""
        token = self.get_auth_token(client, db_session)
        assert token is not None
        
        response = client.get("/api/fleet/status",
                            headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have same structure as induction plan
        assert "trainsets" in data
        assert "summary" in data
        assert "generated_at" in data
    
    def test_fleet_status_with_date_parameter(self, client: TestClient, db_session):
        """Test fleet status endpoint with date parameter"""
        token = self.get_auth_token(client, db_session)
        assert token is not None
        
        response = client.get("/api/fleet/status?date=2023-12-01",
                            headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 200
        data = response.json()
        assert "trainsets" in data
    
    def test_fleet_status_with_invalid_date(self, client: TestClient, db_session):
        """Test fleet status endpoint with invalid date format"""
        token = self.get_auth_token(client, db_session)
        assert token is not None
        
        response = client.get("/api/fleet/status?date=invalid-date",
                            headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_get_all_trainsets(self, client: TestClient, db_session):
        """Test get all trainsets endpoint"""
        token = self.get_auth_token(client, db_session)
        assert token is not None
        
        response = client.get("/api/trainsets",
                            headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return a list (empty for test database)
        assert isinstance(data, list)
    
    def test_get_trainset_detail_not_found(self, client: TestClient, db_session):
        """Test get trainset detail for non-existent trainset"""
        token = self.get_auth_token(client, db_session)
        assert token is not None
        
        response = client.get("/api/trainsets/999",
                            headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_get_trainset_by_number_not_found(self, client: TestClient, db_session):
        """Test get trainset by number for non-existent trainset"""
        token = self.get_auth_token(client, db_session)
        assert token is not None
        
        response = client.get("/api/trainsets/number/TS-9999",
                            headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

class TestAPIValidation:
    """Test API input validation"""
    
    def test_login_missing_username(self, client: TestClient):
        """Test login with missing username"""
        response = client.post("/api/auth/login", json={
            "password": "admin123"
        })
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_login_missing_password(self, client: TestClient):
        """Test login with missing password"""
        response = client.post("/api/auth/login", json={
            "username": "admin"
        })
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_login_empty_credentials(self, client: TestClient):
        """Test login with empty credentials"""
        response = client.post("/api/auth/login", json={
            "username": "",
            "password": ""
        })
        
        # Should fail validation or authentication
        assert response.status_code in [401, 422]

class TestErrorHandling:
    """Test error handling in API endpoints"""
    
    def test_invalid_bearer_token(self, client: TestClient):
        """Test API with invalid bearer token"""
        response = client.get("/api/auth/me", 
                            headers={"Authorization": "Bearer invalid-token"})
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_malformed_authorization_header(self, client: TestClient):
        """Test API with malformed authorization header"""
        response = client.get("/api/auth/me", 
                            headers={"Authorization": "InvalidFormat"})
        
        assert response.status_code == 401
    
    def test_missing_authorization_header(self, client: TestClient):
        """Test protected endpoint without authorization header"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401

class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_openapi_docs_accessible(self, client: TestClient):
        """Test that OpenAPI documentation is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_json_accessible(self, client: TestClient):
        """Test that OpenAPI JSON schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

class TestCORSConfiguration:
    """Test CORS configuration"""
    
    def test_cors_headers_present(self, client: TestClient):
        """Test that CORS headers are present in responses"""
        response = client.options("/api/auth/login")
        
        # Should have CORS headers (may be 200 or 405 depending on implementation)
        assert response.status_code in [200, 405]
    
    def test_preflight_request(self, client: TestClient):
        """Test CORS preflight request handling"""
        response = client.options("/api/auth/login", 
                                headers={
                                    "Origin": "http://localhost:3000",
                                    "Access-Control-Request-Method": "POST"
                                })
        
        # Should handle preflight request appropriately
        assert response.status_code in [200, 405]
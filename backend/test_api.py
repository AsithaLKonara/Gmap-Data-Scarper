#!/usr/bin/env python3
"""
Comprehensive API tests for LeadTap backend
"""

import pytest
from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

class TestHealthEndpoints:
    """Test health and basic endpoints"""
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"

class TestAuthenticationEndpoints:
    """Test authentication endpoints"""
    
    def test_user_me_unauthorized(self):
        """Test user endpoint without authentication"""
        response = client.get("/api/auth/user/me")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Not authenticated"

class TestJobsEndpoints:
    """Test jobs/scraping endpoints"""
    
    def test_jobs_unauthorized(self):
        """Test jobs endpoint without authentication"""
        response = client.get("/api/scrape/jobs")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Not authenticated"
    
    def test_create_job_unauthorized(self):
        """Test job creation without authentication"""
        job_data = {
            "queries": ["coffee shops in New York"]
        }
        response = client.post("/api/scrape/", json=job_data)
        assert response.status_code == 401

class TestLeadScoringEndpoints:
    """Test lead scoring endpoints"""
    
    def test_scoring_criteria(self):
        """Test getting scoring criteria"""
        response = client.get("/api/lead-scoring/criteria")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check structure of criteria
        for criterion in data:
            assert "name" in criterion
            assert "weight" in criterion
            assert "description" in criterion
            assert 0 <= criterion["weight"] <= 1

class TestWhatsAppEndpoints:
    """Test WhatsApp workflow endpoints"""
    
    def test_whatsapp_workflows_unauthorized(self):
        """Test WhatsApp workflows without authentication"""
        response = client.get("/api/whatsapp/workflows")
        assert response.status_code == 401

class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_docs_endpoint(self):
        """Test the API documentation endpoint"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_endpoint(self):
        """Test the ReDoc documentation endpoint"""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

class TestErrorHandling:
    """Test error handling"""
    
    def test_404_endpoint(self):
        """Test 404 handling"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_json(self):
        """Test invalid JSON handling"""
        response = client.post("/api/scrape/", data="invalid json")
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
 
"""
Comprehensive API tests for LeadTap backend
"""

import pytest
from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

class TestHealthEndpoints:
    """Test health and basic endpoints"""
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"

class TestAuthenticationEndpoints:
    """Test authentication endpoints"""
    
    def test_user_me_unauthorized(self):
        """Test user endpoint without authentication"""
        response = client.get("/api/auth/user/me")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Not authenticated"

class TestJobsEndpoints:
    """Test jobs/scraping endpoints"""
    
    def test_jobs_unauthorized(self):
        """Test jobs endpoint without authentication"""
        response = client.get("/api/scrape/jobs")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Not authenticated"
    
    def test_create_job_unauthorized(self):
        """Test job creation without authentication"""
        job_data = {
            "queries": ["coffee shops in New York"]
        }
        response = client.post("/api/scrape/", json=job_data)
        assert response.status_code == 401

class TestLeadScoringEndpoints:
    """Test lead scoring endpoints"""
    
    def test_scoring_criteria(self):
        """Test getting scoring criteria"""
        response = client.get("/api/lead-scoring/criteria")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check structure of criteria
        for criterion in data:
            assert "name" in criterion
            assert "weight" in criterion
            assert "description" in criterion
            assert 0 <= criterion["weight"] <= 1

class TestWhatsAppEndpoints:
    """Test WhatsApp workflow endpoints"""
    
    def test_whatsapp_workflows_unauthorized(self):
        """Test WhatsApp workflows without authentication"""
        response = client.get("/api/whatsapp/workflows")
        assert response.status_code == 401

class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_docs_endpoint(self):
        """Test the API documentation endpoint"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_endpoint(self):
        """Test the ReDoc documentation endpoint"""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

class TestErrorHandling:
    """Test error handling"""
    
    def test_404_endpoint(self):
        """Test 404 handling"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_json(self):
        """Test invalid JSON handling"""
        response = client.post("/api/scrape/", data="invalid json")
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
 
"""
Comprehensive API tests for LeadTap backend
"""

import pytest
from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

class TestHealthEndpoints:
    """Test health and basic endpoints"""
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"

class TestAuthenticationEndpoints:
    """Test authentication endpoints"""
    
    def test_user_me_unauthorized(self):
        """Test user endpoint without authentication"""
        response = client.get("/api/auth/user/me")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Not authenticated"

class TestJobsEndpoints:
    """Test jobs/scraping endpoints"""
    
    def test_jobs_unauthorized(self):
        """Test jobs endpoint without authentication"""
        response = client.get("/api/scrape/jobs")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Not authenticated"
    
    def test_create_job_unauthorized(self):
        """Test job creation without authentication"""
        job_data = {
            "queries": ["coffee shops in New York"]
        }
        response = client.post("/api/scrape/", json=job_data)
        assert response.status_code == 401

class TestLeadScoringEndpoints:
    """Test lead scoring endpoints"""
    
    def test_scoring_criteria(self):
        """Test getting scoring criteria"""
        response = client.get("/api/lead-scoring/criteria")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check structure of criteria
        for criterion in data:
            assert "name" in criterion
            assert "weight" in criterion
            assert "description" in criterion
            assert 0 <= criterion["weight"] <= 1

class TestWhatsAppEndpoints:
    """Test WhatsApp workflow endpoints"""
    
    def test_whatsapp_workflows_unauthorized(self):
        """Test WhatsApp workflows without authentication"""
        response = client.get("/api/whatsapp/workflows")
        assert response.status_code == 401

class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_docs_endpoint(self):
        """Test the API documentation endpoint"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_endpoint(self):
        """Test the ReDoc documentation endpoint"""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

class TestErrorHandling:
    """Test error handling"""
    
    def test_404_endpoint(self):
        """Test 404 handling"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_json(self):
        """Test invalid JSON handling"""
        response = client.post("/api/scrape/", data="invalid json")
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
 
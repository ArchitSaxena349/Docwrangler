"""
API endpoint tests
"""
import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "LLM DocWrangler API"


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


def test_detailed_health_endpoint(client):
    """Test detailed health check endpoint"""
    response = client.get("/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "checks" in data
    assert "gemini_api" in data["checks"]
    assert "vector_store" in data["checks"]


def test_readiness_endpoint(client):
    """Test readiness probe"""
    response = client.get("/readiness")
    # May return 503 if Gemini API not configured
    assert response.status_code in [200, 503]


def test_liveness_endpoint(client):
    """Test liveness probe"""
    response = client.get("/liveness")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_webhook_health_endpoint(client):
    """Test webhook health endpoint (backward compatibility)"""
    response = client.get("/webhook/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "endpoints" in data


def test_webhook_query_endpoint(client, sample_query_payload):
    """Test webhook query endpoint"""
    response = client.post("/webhook/query", json=sample_query_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "query" in data
    assert "decision" in data
    assert "confidence" in data


def test_webhook_insurance_claim_endpoint(client, sample_claim_payload):
    """Test webhook insurance claim endpoint"""
    response = client.post("/webhook/insurance-claim", json=sample_claim_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert "decision" in data
    assert "coverage_amount" in data


def test_webhook_document_upload_endpoint(client):
    """Test webhook document upload endpoint"""
    payload = {
        "file_path": "/path/to/document.pdf",
        "callback_url": "https://example.com/callback",
        "metadata": {"source": "test"}
    }
    
    # Patch os.path.exists to simulate file existence
    import unittest.mock
    with unittest.mock.patch("os.path.exists", return_value=True):
        response = client.post("/webhook/document-upload", json=payload)
        
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert "document_id" in data


def test_request_id_header(client):
    """Test that request ID is added to response headers"""
    response = client.get("/health")
    assert "X-Request-ID" in response.headers


def test_cors_headers(client):
    """Test CORS headers are present"""
    headers = {"Origin": "http://localhost"}
    response = client.get("/health", headers=headers)
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "*"

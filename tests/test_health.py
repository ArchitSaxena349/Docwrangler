"""
Health check specific tests
"""
import pytest


def test_health_check_structure(client):
    """Test health check response structure"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    required_fields = ["status", "timestamp", "version", "dependencies"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"


def test_detailed_health_check_dependencies(client):
    """Test detailed health check includes all dependency checks"""
    response = client.get("/health/detailed")
    assert response.status_code == 200
    
    data = response.json()
    checks = data["checks"]
    
    required_checks = ["gemini_api", "vector_store", "embedding_model", "file_system"]
    for check in required_checks:
        assert check in checks, f"Missing health check: {check}"
        assert "status" in checks[check], f"Missing status in {check}"


def test_health_status_values(client):
    """Test health status has valid values"""
    response = client.get("/health/detailed")
    assert response.status_code == 200
    
    data = response.json()
    valid_statuses = ["healthy", "degraded", "unhealthy"]
    assert data["status"] in valid_statuses


def test_liveness_always_succeeds(client):
    """Test liveness probe always returns success"""
    response = client.get("/liveness")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"

"""
Integration tests for end-to-end workflows
"""
import pytest


def test_query_workflow(client, sample_query_payload):
    """Test complete query workflow"""
    # Test query processing
    response = client.post("/webhook/query", json=sample_query_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert data["query"] == sample_query_payload["query"]
    assert "decision" in data
    assert "justification" in data
    
    # Verify decision is one of expected values
    assert data["decision"] in ["approved", "rejected", "pending"]


def test_insurance_claim_workflow(client, sample_claim_payload):
    """Test complete insurance claim workflow"""
    response = client.post("/webhook/insurance-claim", json=sample_claim_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "processed"
    assert data["claim_id"] == sample_claim_payload["claim_id"]
    assert "decision" in data
    assert "coverage_amount" in data
    assert "justification" in data


def test_surgery_claim_approval(client):
    """Test that surgery claims are typically approved"""
    payload = {
        "age": 30,
        "gender": "female",
        "procedure": "knee surgery",
        "location": "Delhi",
        "claim_amount": 80000
    }
    
    response = client.post("/webhook/insurance-claim", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["decision"] == "approved"
    assert data["coverage_amount"] > 0


def test_dental_claim_rejection(client):
    """Test that dental claims require verification"""
    payload = {
        "age": 25,
        "gender": "male",
        "procedure": "dental filling",
        "location": "Mumbai",
        "claim_amount": 5000
    }
    
    response = client.post("/webhook/insurance-claim", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["decision"] == "rejected"
    assert data["coverage_amount"] == 0


def test_multiple_requests_with_different_ids(client, sample_query_payload):
    """Test that multiple requests get different request IDs"""
    response1 = client.post("/webhook/query", json=sample_query_payload)
    response2 = client.post("/webhook/query", json=sample_query_payload)
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    request_id1 = response1.headers.get("X-Request-ID")
    request_id2 = response2.headers.get("X-Request-ID")
    
    assert request_id1 != request_id2

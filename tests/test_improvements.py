import pytest
import hmac
import hashlib
import os
import unittest.mock
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from src.core.models import QueryRequest, QueryType, DecisionResult, ParsedQuery
from src.decision_engine.rules import RulesEngine
from src.retrieval.hybrid_search import HybridSearcher, RetrievalResult

def test_deterministic_rules_exclusions():
    """Verify that standard exclusions trigger immediate rejection without LLM"""
    parsed_query = ParsedQuery(
        original_query="I want cosmetic surgery treatment coverage",
        structured_data={"medical_procedure": "cosmetic surgery"},
        query_type=QueryType.INSURANCE_CLAIM,
        key_entities=["cosmetic surgery"],
        intent="approval_check"
    )
    
    result = RulesEngine.evaluate_rules(parsed_query)
    assert result is not None
    assert result.decision == "rejected"
    assert "cosmetic surgery" in result.justification.lower()
    assert result.confidence_score == 1.0

def test_deterministic_rules_age_escalation():
    """Verify that extreme age (e.g. >99) flags claim for manual review"""
    parsed_query = ParsedQuery(
        original_query="Knee replacement for 105 year old patient",
        structured_data={"age": 105, "medical_procedure": "knee replacement"},
        query_type=QueryType.INSURANCE_CLAIM,
        key_entities=["knee replacement"],
        intent="approval_check"
    )
    
    result = RulesEngine.evaluate_rules(parsed_query)
    assert result is not None
    assert result.decision == "pending"
    assert "manual" in result.justification.lower()

def test_deterministic_rules_amount_escalation():
    """Verify that claims exceeding standard caps are escalated"""
    parsed_query = ParsedQuery(
        original_query="Claim amount $125,000 for surgery",
        structured_data={"amount": 125000.0, "medical_procedure": "surgery"},
        query_type=QueryType.INSURANCE_CLAIM,
        key_entities=["surgery"],
        intent="approval_check"
    )
    
    result = RulesEngine.evaluate_rules(parsed_query)
    assert result is not None
    assert result.decision == "pending"
    assert "escalated" in result.justification.lower()

def test_hmac_webhook_signature_required(client):
    """Verify webhook blocks request if signature key is set but signature is missing"""
    os.environ["WEBHOOK_SECRET"] = "super_secret_webhook_key"
    try:
        response = client.post("/webhook/query", json={"query": "test query"})
        assert response.status_code == 401
        assert "signature" in response.json()["detail"].lower()
    finally:
        del os.environ["WEBHOOK_SECRET"]

def test_hmac_webhook_signature_invalid(client):
    """Verify webhook blocks request if signature is invalid"""
    os.environ["WEBHOOK_SECRET"] = "super_secret_webhook_key"
    try:
        headers = {"x-signature": "wrong_signature"}
        response = client.post("/webhook/query", json={"query": "test query"}, headers=headers)
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
    finally:
        del os.environ["WEBHOOK_SECRET"]

def test_hmac_webhook_signature_valid(client):
    """Verify webhook accepts request with valid signature"""
    os.environ["WEBHOOK_SECRET"] = "super_secret_webhook_key"
    payload = {"query": "Is appendicitis surgery covered?"}
    import json
    body_bytes = json.dumps(payload).encode("utf-8")
    
    # Calculate valid signature
    sig = hmac.new(
        b"super_secret_webhook_key",
        body_bytes,
        hashlib.sha256
    ).hexdigest()
    
    headers = {"x-signature": sig}
    try:
        # Patch query service so it executes cleanly
        with unittest.mock.patch("main.get_query_service") as mock_get_service:
            mock_service = MagicMock()
            mock_get_service.return_value = mock_service
            
            async def mock_query(req):
                from src.core.models import DecisionResult
                return MagicMock(
                    query=req.query,
                    decision=DecisionResult(
                        decision="approved",
                        payment_mode="Cashless",
                        amount=50000,
                        justification="Test",
                        source_clauses=[],
                        confidence_score=0.9
                    ),
                    processing_time=0.1
                )
            mock_service.process_query.side_effect = mock_query
            
            response = client.post("/webhook/query", content=body_bytes, headers=headers)
            assert response.status_code == 200
            assert response.json()["status"] == "success"
    finally:
        del os.environ["WEBHOOK_SECRET"]

def test_reciprocal_rank_fusion():
    """Verify RRF ranking combines results correctly"""
    vector_results = [
        RetrievalResult(chunk_id="chunk1", document_id="doc1", content="A", similarity_score=0.9, metadata={}),
        RetrievalResult(chunk_id="chunk2", document_id="doc1", content="B", similarity_score=0.8, metadata={})
    ]
    bm25_results = [
        RetrievalResult(chunk_id="chunk3", document_id="doc1", content="C", similarity_score=0.9, metadata={}),
        RetrievalResult(chunk_id="chunk1", document_id="doc1", content="A", similarity_score=0.8, metadata={})
    ]
    
    searcher = HybridSearcher(vector_store=MagicMock())
    # chunk1 is rank 1 in vector, rank 2 in bm25 -> RRF should rank it highest
    merged = searcher._reciprocal_rank_fusion(vector_results, bm25_results, top_k=2)
    assert len(merged) == 2
    assert merged[0].chunk_id == "chunk1"

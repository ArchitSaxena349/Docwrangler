"""
Pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
import os
import sys
from unittest.mock import MagicMock
import unittest

# Set test environment variables
os.environ["GEMINI_API_KEY"] = "test_key"
os.environ["LOG_LEVEL"] = "ERROR"

# Mock heavy dependencies that might be missing
sys.modules["chromadb"] = MagicMock()
sys.modules["chromadb.config"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()

from main import app
from core.models import DecisionResult, ParsedQuery, QueryType, ProcessingResponse

@pytest.fixture(autouse=True)
def mock_services():
    """Mock the services to avoid real logic/dependencies"""
    # Patch the class where it is USED in main.py
    with unittest.mock.patch("main.QueryService") as MockQueryService:
        # Setup the mock instance
        mock_service = MockQueryService.return_value
        
        async def process_query(request):
            query_text = request.query.lower()
            
            # Default decision
            decision = "pending"
            amount = None
            justification = "Pending review"
            
            if "surgery" in query_text:
                decision = "approved"
                amount = 80000
                justification = "Surgery approved"
            elif "dental" in query_text:
                decision = "rejected"
                amount = 0
                justification = "Dental rejected"
            elif "maternity" in query_text:
                decision = "approved"
                amount = 75000
                justification = "Maternity approved"
                
            return ProcessingResponse(
                query=request.query,
                parsed_query=ParsedQuery(
                    original_query=request.query,
                    structured_data={},
                    query_type=QueryType.GENERAL,
                    key_entities=[],
                    intent="test"
                ),
                retrieved_documents=[],
                decision=DecisionResult(
                    decision=decision,
                    amount=amount,
                    justification=justification,
                    source_clauses=["test_clause"],
                    confidence_score=0.9,
                    metadata={}
                ),
                processing_time=0.1
            )
            
        mock_service.process_query.side_effect = process_query
        
        # Manually inject into main module to ensure it's set
        import main
        main.query_service = mock_service
        main.document_service = MagicMock()
        
        async def mock_process_doc(path):
            return "doc_123"
        main.document_service.process_document.side_effect = mock_process_doc
        
        yield


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def sample_query_payload():
    """Sample query payload for testing"""
    return {
        "query": "Is surgery for appendicitis covered?",
        "context": {"policy_id": "POL123"}
    }


@pytest.fixture
def sample_claim_payload():
    """Sample insurance claim payload for testing"""
    return {
        "claim_id": "CLM-TEST-001",
        "age": 35,
        "gender": "male",
        "procedure": "appendix surgery",
        "location": "Mumbai",
        "policy_duration": "2 years",
        "claim_amount": 75000
    }

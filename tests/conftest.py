"""
Pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
import os
import sys
from unittest.mock import MagicMock

# Set test environment variables
os.environ["GEMINI_API_KEY"] = "test_key"
os.environ["LOG_LEVEL"] = "ERROR"

# Mock heavy dependencies that might be missing
sys.modules["chromadb"] = MagicMock()
sys.modules["chromadb.config"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()

from main import app


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

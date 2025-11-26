from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class QueryType(str, Enum):
    INSURANCE_CLAIM = "insurance_claim"
    CONTRACT_REVIEW = "contract_review"
    POLICY_CHECK = "policy_check"
    GENERAL = "general"

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    EMAIL = "email"
    TEXT = "text"
    IMAGE = "image"

class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    document_ids: Optional[List[str]] = Field(None, description="Specific document IDs to search")
    query_type: Optional[QueryType] = Field(QueryType.GENERAL, description="Type of query")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class ParsedQuery(BaseModel):
    original_query: str
    structured_data: Dict[str, Any]
    query_type: QueryType
    key_entities: List[str]
    intent: str

class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

class RetrievalResult(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    similarity_score: float
    metadata: Dict[str, Any]

class DecisionResult(BaseModel):
    decision: str = Field(..., description="Final decision (approved/rejected/pending)")
    payment_mode: str = Field(..., description="Payment mode (Cashless/Reimbursement/Unknown)")
    amount: Optional[float] = Field(None, description="Amount if applicable")
    justification: str = Field(..., description="Explanation of the decision")
    source_clauses: List[str] = Field(..., description="Referenced document clauses")
    confidence_score: float = Field(..., description="Confidence in the decision (0-1)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ProcessingResponse(BaseModel):
    query: str
    parsed_query: ParsedQuery
    retrieved_documents: List[RetrievalResult]
    decision: DecisionResult
    processing_time: float
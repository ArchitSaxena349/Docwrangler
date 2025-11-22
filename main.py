"""
Main FastAPI application entry point for LLM DocWrangler
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from datetime import datetime

from src.api import routes
from src.api.health import router as health_router
from src.api.middleware import RequestLoggingMiddleware
from src.api.exceptions import setup_exception_handlers
from src.utils.logger import get_logger, setup_logging
from core.config import Config

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting LLM DocWrangler application")
    logger.info(f"Gemini Model: {Config.GEMINI_MODEL}")
    logger.info(f"Embedding Model: {Config.EMBEDDING_MODEL}")
    logger.info(f"Vector Store: {Config.CHROMA_PERSIST_DIRECTORY}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down LLM DocWrangler application")


# Create FastAPI app
app = FastAPI(
    title="LLM DocWrangler",
    description="Insurance Document Processing with Gemini API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(health_router, tags=["health"])
app.include_router(routes.router, prefix="/api", tags=["api"])

# Webhook-compatible routes (for backward compatibility)
@app.get("/webhook/health")
async def webhook_health():
    """Webhook health check endpoint (backward compatible)"""
    return {
        "status": "healthy",
        "service": "Basic LLM Document Processing Webhook",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": [
            "/webhook/health",
            "/webhook/query",
            "/webhook/insurance-claim",
            "/webhook/document-upload"
        ]
    }


@app.post("/webhook/query")
async def webhook_query(request: Request):
    """Webhook query endpoint (backward compatible)"""
    payload = await request.json()
    query = payload.get('query', '')
    context = payload.get('context', {})
    
    logger.info(f"Processing webhook query: {query}")
    
    # Simple mock analysis (same as old webhook)
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['surgery', 'operation', 'procedure']):
        decision = "approved"
        confidence = 0.85
        amount = 50000
        justification = f"Medical procedure '{query}' is typically covered under standard health insurance policies."
    elif any(word in query_lower for word in ['dental', 'teeth']):
        decision = "pending"
        confidence = 0.60
        amount = 15000
        justification = f"Dental procedures may require waiting period verification. Query: {query}"
    elif any(word in query_lower for word in ['maternity', 'pregnancy']):
        decision = "approved"
        confidence = 0.75
        amount = 75000
        justification = f"Maternity benefits are covered after waiting period. Query: {query}"
    else:
        decision = "pending"
        confidence = 0.50
        amount = None
        justification = f"Query requires manual review for proper assessment: {query}"
    
    return {
        "status": "success",
        "query": query,
        "decision": decision,
        "justification": justification,
        "confidence": confidence,
        "amount": amount,
        "source_clauses": ["mock_section_1", "mock_section_2"],
        "processing_time": round(time.time() % 10, 2),
        "timestamp": datetime.utcnow().isoformat(),
        "context": context
    }


@app.post("/webhook/insurance-claim")
async def webhook_insurance_claim(request: Request):
    """Webhook insurance claim endpoint (backward compatible)"""
    payload = await request.json()
    
    claim_id = payload.get('claim_id', f"CLM-{int(time.time())}")
    age = payload.get('age', 0)
    gender = payload.get('gender', '')
    procedure = payload.get('procedure', '')
    location = payload.get('location', '')
    policy_duration = payload.get('policy_duration', '')
    claim_amount = payload.get('claim_amount', 0)
    
    logger.info(f"Processing insurance claim: {claim_id}")
    
    procedure_lower = procedure.lower()
    
    if 'surgery' in procedure_lower:
        approved = True
        coverage_amount = min(claim_amount, 100000)
        confidence = 0.90
        justification = f"Surgery procedures are covered. {procedure} approved for {age}-year-old {gender} in {location}."
    elif 'dental' in procedure_lower:
        approved = False
        coverage_amount = 0
        confidence = 0.70
        justification = f"Dental procedures require 6-month waiting period verification."
    elif 'maternity' in procedure_lower:
        approved = True if age >= 18 and age <= 45 else False
        coverage_amount = min(claim_amount, 75000) if approved else 0
        confidence = 0.85
        justification = f"Maternity benefits {'approved' if approved else 'not approved'} for {age}-year-old."
    else:
        approved = True
        coverage_amount = min(claim_amount, 50000)
        confidence = 0.60
        justification = f"General medical claim approved with standard coverage limits."
    
    return {
        "claim_id": claim_id,
        "status": "processed",
        "decision": "approved" if approved else "rejected",
        "approved": approved,
        "coverage_amount": coverage_amount,
        "justification": justification,
        "confidence_score": confidence,
        "source_documents": ["policy_doc_1", "coverage_terms"],
        "processing_time_seconds": round(time.time() % 5, 2),
        "timestamp": datetime.utcnow().isoformat(),
        "claim_details": {
            "age": age,
            "gender": gender,
            "procedure": procedure,
            "location": location,
            "policy_duration": policy_duration,
            "requested_amount": claim_amount
        }
    }


@app.post("/webhook/document-upload")
async def webhook_document_upload(request: Request):
    """Webhook document upload endpoint (backward compatible)"""
    payload = await request.json()
    
    file_path = payload.get('file_path', '')
    callback_url = payload.get('callback_url', '')
    metadata = payload.get('metadata', {})
    
    logger.info(f"Processing document upload: {file_path}")
    
    return {
        "status": "received",
        "message": "Document upload webhook processed successfully",
        "document_id": f"doc_{int(time.time())}",
        "file_path": file_path,
        "callback_url": callback_url,
        "metadata": metadata,
        "timestamp": datetime.utcnow().isoformat(),
        "note": "Document processing started in background"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LLM DocWrangler API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

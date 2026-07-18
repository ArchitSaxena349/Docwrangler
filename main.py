"""
Main FastAPI application entry point for LLM DocWrangler
"""
from fastapi import FastAPI, Request, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from datetime import datetime, timezone
import os

from src.api import routes
from src.api.health import router as health_router
from src.api.middleware import RequestLoggingMiddleware
from src.api.exceptions import setup_exception_handlers
from src.utils.logger import get_logger, setup_logging
from src.core.config import Config
from src.core.models import QueryRequest, QueryType
from src.api.dependencies import get_query_service, get_document_service, init_services

# Setup logging
setup_logging()
logger = get_logger(__name__)

# API Key Security
API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """Validate API Key"""
    # If no API key is set in env, allow all (dev mode)
    expected_key = os.getenv("APP_API_KEY")
    if not expected_key:
        return None
        
    if api_key_header == expected_key:
        return api_key_header
        
    raise HTTPException(
        status_code=403,
        detail="Could not validate credentials"
    )

from src.utils.cloud_sync import CloudSyncService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting LLM DocWrangler application")
    logger.info(f"Groq Model: {Config.GROQ_MODEL}")
    logger.info(f"Groq Vision Model: {Config.GROQ_VISION_MODEL}")
    logger.info(f"Embedding Model: {Config.EMBEDDING_MODEL}")
    logger.info(f"Vector Store: {Config.CHROMA_PERSIST_DIRECTORY}")
    
    # Pre-startup: Download vector store backup if S3 is configured
    try:
        CloudSyncService.download_vector_store()
    except Exception as e:
        logger.error(f"Error restoring vector database from cloud: {e}", exc_info=True)
    
    # Initialize services
    try:
        init_services()
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
    
    yield
    
    # Shutdown: Backup vector store
    logger.info("Shutting down LLM DocWrangler application")
    try:
        CloudSyncService.upload_vector_store()
    except Exception as e:
        logger.error(f"Error backing up vector database to cloud: {e}", exc_info=True)


# Create FastAPI app
app = FastAPI(
    title="LLM DocWrangler",
    description="Insurance Document Processing with Groq API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
allowed_origins = Config.ALLOWED_ORIGINS if Config.ALLOWED_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True if allowed_origins and "*" not in allowed_origins else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(health_router, tags=["health"])
# Protect API routes with API Key
app.include_router(
    routes.router, 
    prefix="/api", 
    tags=["api"],
    dependencies=[Depends(get_api_key)]
)

# Webhook-compatible routes (for backward compatibility)
# These are now powered by the real services!

@app.get("/webhook/health")
async def webhook_health():
    """Webhook health check endpoint (backward compatible)"""
    return {
        "status": "healthy",
        "service": "LLM Document Processing Webhook (FastAPI)",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": [
            "/webhook/health",
            "/webhook/query",
            "/webhook/insurance-claim",
            "/webhook/document-upload"
        ]
    }


import hmac
import hashlib

async def set_body(request: Request, body: bytes):
    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}
    request._receive = receive

async def verify_webhook_signature(request: Request):
    """Optional validation of webhook HMAC signature using WEBHOOK_SECRET"""
    webhook_secret = os.getenv("WEBHOOK_SECRET")
    if not webhook_secret:
        return
        
    signature = request.headers.get("x-signature")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing x-signature header")
        
    body = await request.body()
    await set_body(request, body) # cache body so request.json() can read it again
    
    expected_signature = hmac.new(
        webhook_secret.encode("utf-8"),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")


@app.post("/webhook/query", dependencies=[Depends(verify_webhook_signature)])
async def webhook_query(request: Request):
    """Webhook query endpoint (powered by Groq)"""
    try:
        payload = await request.json()
        query_text = payload.get('query', '')
        context = payload.get('context', {})
        
        logger.info(f"Processing webhook query: {query_text}")
        
        query_service = get_query_service()
        if not query_service:
            raise HTTPException(status_code=503, detail="Query service not initialized")
            
        # Create request object
        query_request = QueryRequest(
            query=query_text,
            context=context,
            query_type=QueryType.GENERAL
        )
        
        # Process using real service
        result = await query_service.process_query(query_request)
        
        # Map response to match old webhook format
        return {
            "status": "success",
            "query": result.query,
            "decision": result.decision.decision,
            "justification": result.decision.justification,
            "confidence": result.decision.confidence_score,
            "amount": result.decision.amount,
            "source_clauses": result.decision.source_clauses,
            "processing_time": result.processing_time,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": context
        }
    except Exception as e:
        logger.error(f"Error in webhook query: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@app.post("/webhook/insurance-claim", dependencies=[Depends(verify_webhook_signature)])
async def webhook_insurance_claim(request: Request):
    """Webhook insurance claim endpoint (powered by Groq)"""
    try:
        payload = await request.json()
        
        claim_id = payload.get('claim_id', f"CLM-{int(time.time())}")
        procedure = payload.get('procedure', '')
        
        # Construct a natural language query from the claim details
        query_text = f"Evaluate insurance claim {claim_id} for {procedure}. "
        if 'age' in payload:
            query_text += f"Patient age: {payload['age']}. "
        if 'location' in payload:
            query_text += f"Location: {payload['location']}. "
        if 'claim_amount' in payload:
            query_text += f"Amount: {payload['claim_amount']}. "
            
        logger.info(f"Processing insurance claim via Groq: {claim_id}")
        
        query_service = get_query_service()
        if not query_service:
            raise HTTPException(status_code=503, detail="Query service not initialized")
            
        # Create request object
        query_request = QueryRequest(
            query=query_text,
            context=payload,
            query_type=QueryType.INSURANCE_CLAIM
        )
        
        # Process using real service
        result = await query_service.process_query(query_request)
        
        # Map response to match old webhook format
        is_approved = result.decision.decision.lower() == "approved"
        
        return {
            "claim_id": claim_id,
            "status": "processed",
            "decision": result.decision.decision,
            "approved": is_approved,
            "coverage_amount": result.decision.amount,
            "justification": result.decision.justification,
            "confidence_score": result.decision.confidence_score,
            "source_documents": result.decision.source_clauses,
            "processing_time_seconds": result.processing_time,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "claim_details": payload
        }
    except Exception as e:
        logger.error(f"Error in insurance claim webhook: {e}")
        return {
            "status": "error",
            "message": str(e),
            "claim_id": payload.get('claim_id')
        }


@app.post("/webhook/document-upload", dependencies=[Depends(verify_webhook_signature)])
async def webhook_document_upload(request: Request):
    """Webhook document upload endpoint (powered by DocumentService)"""
    # Note: This endpoint expects a file path in JSON, which assumes the file 
    # is already on the server. Real file upload should use /api/upload
    try:
        payload = await request.json()
        file_path = payload.get('file_path', '')
        
        logger.info(f"Processing document upload request: {file_path}")
        
        document_service = get_document_service()
        if not document_service:
            raise HTTPException(status_code=503, detail="Document service not initialized")
            
        if os.path.exists(file_path):
            document_id = await document_service.process_document(file_path)
            status = "processed"
            message = "Document processed successfully"
        else:
            document_id = None
            status = "error"
            message = "File not found at specified path"
            
        return {
            "status": status,
            "message": message,
            "document_id": document_id,
            "file_path": file_path,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error in document upload webhook: {e}")
        return {
            "status": "error",
            "message": str(e)
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
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

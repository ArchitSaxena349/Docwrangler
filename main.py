"""
Main FastAPI application entry point for LLM DocWrangler
"""
from fastapi import FastAPI, Request, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from datetime import datetime
import os

from src.api import routes
from src.api.health import router as health_router
from src.api.middleware import RequestLoggingMiddleware
from src.api.exceptions import setup_exception_handlers
from src.utils.logger import get_logger, setup_logging
from core.config import Config
from core.models import QueryRequest, QueryType

# Import services
from src.services.query_service import QueryService
from src.services.document_service import DocumentService

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize services
query_service = None
document_service = None

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting LLM DocWrangler application")
    logger.info(f"Gemini Model: {Config.GEMINI_MODEL}")
    logger.info(f"Embedding Model: {Config.EMBEDDING_MODEL}")
    logger.info(f"Vector Store: {Config.CHROMA_PERSIST_DIRECTORY}")
    
    # Initialize services
    global query_service, document_service
    try:
        query_service = QueryService()
        document_service = DocumentService()
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
    
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
    """Webhook query endpoint (powered by Gemini)"""
    try:
        payload = await request.json()
        query_text = payload.get('query', '')
        context = payload.get('context', {})
        
        logger.info(f"Processing webhook query: {query_text}")
        
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
            "timestamp": datetime.utcnow().isoformat(),
            "context": context
        }
    except Exception as e:
        logger.error(f"Error in webhook query: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@app.post("/webhook/insurance-claim")
async def webhook_insurance_claim(request: Request):
    """Webhook insurance claim endpoint (powered by Gemini)"""
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
            
        logger.info(f"Processing insurance claim via Gemini: {claim_id}")
        
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
            "timestamp": datetime.utcnow().isoformat(),
            "claim_details": payload
        }
    except Exception as e:
        logger.error(f"Error in insurance claim webhook: {e}")
        return {
            "status": "error",
            "message": str(e),
            "claim_id": payload.get('claim_id')
        }


@app.post("/webhook/document-upload")
async def webhook_document_upload(request: Request):
    """Webhook document upload endpoint (powered by DocumentService)"""
    # Note: This endpoint expects a file path in JSON, which assumes the file 
    # is already on the server. Real file upload should use /api/upload
    try:
        payload = await request.json()
        file_path = payload.get('file_path', '')
        
        logger.info(f"Processing document upload request: {file_path}")
        
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
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in document upload webhook: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/api/health")
async def api_health_check():
    """API Health check endpoint"""
    return {"status": "healthy", "service": "LLM Document Processing System"}

# Mount frontend static files
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount static files (JS, CSS, images)
if os.path.exists("frontend/dist"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve the frontend application"""
    # If API route, let it pass through (handled by other routers)
    if full_path.startswith("api") or full_path.startswith("webhook") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
        raise HTTPException(status_code=404, detail="Not Found")
    
    # Serve index.html for all other routes (SPA)
    if os.path.exists("frontend/dist/index.html"):
        return FileResponse("frontend/dist/index.html")
    
    return {
        "message": "LLM DocWrangler API (Frontend not built)",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

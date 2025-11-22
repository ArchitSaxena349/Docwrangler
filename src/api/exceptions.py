"""
Custom exceptions for the application
"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import traceback

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentNotFoundError(Exception):
    """Raised when a document is not found"""
    pass


class ProcessingError(Exception):
    """Raised when document processing fails"""
    pass


class VectorStoreError(Exception):
    """Raised when vector store operations fail"""
    pass


class GeminiAPIError(Exception):
    """Raised when Gemini API calls fail"""
    pass


def setup_exception_handlers(app):
    """Setup global exception handlers for the FastAPI app"""
    
    @app.exception_handler(DocumentNotFoundError)
    async def document_not_found_handler(request: Request, exc: DocumentNotFoundError):
        logger.error(f"Document not found: {exc}")
        return JSONResponse(
            status_code=404,
            content={
                "error": "Document not found",
                "detail": str(exc),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @app.exception_handler(ProcessingError)
    async def processing_error_handler(request: Request, exc: ProcessingError):
        logger.error(f"Processing error: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Processing failed",
                "detail": str(exc),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @app.exception_handler(VectorStoreError)
    async def vector_store_error_handler(request: Request, exc: VectorStoreError):
        logger.error(f"Vector store error: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Vector store operation failed",
                "detail": str(exc),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @app.exception_handler(GeminiAPIError)
    async def gemini_api_error_handler(request: Request, exc: GeminiAPIError):
        logger.error(f"Gemini API error: {exc}")
        return JSONResponse(
            status_code=503,
            content={
                "error": "Gemini API unavailable",
                "detail": str(exc),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

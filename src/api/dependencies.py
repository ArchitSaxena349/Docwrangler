from functools import lru_cache
from src.services.document_service import DocumentService
from src.services.query_service import QueryService

# Global instances (can be initialized at startup)
_document_service = None
_query_service = None

def get_document_service() -> DocumentService:
    """Get or create DocumentService instance"""
    global _document_service
    if _document_service is None:
        _document_service = DocumentService()
    return _document_service

def get_query_service() -> QueryService:
    """Get or create QueryService instance"""
    global _query_service
    if _query_service is None:
        _query_service = QueryService()
    return _query_service

def init_services():
    """Initialize services explicitly (e.g. at startup)"""
    get_document_service()
    get_query_service()

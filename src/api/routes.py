from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Optional
import os
import time
from pathlib import Path

from core.models import QueryRequest, ProcessingResponse
from src.api.dependencies import get_document_service, get_query_service
from core.config import Config

router = APIRouter()

@router.post("/upload", response_model=dict)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Validate file type
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ['.pdf', '.docx', '.doc', '.eml', '.msg', '.txt']:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Save uploaded file
        upload_path = Path(Config.UPLOAD_DIRECTORY)
        upload_path.mkdir(exist_ok=True)
        
        file_path = upload_path / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            if len(content) > Config.MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="File too large")
            buffer.write(content)
        
        # Process document
        service = get_document_service()
        document_id = await service.process_document(str(file_path))
        
        return {
            "message": "Document uploaded and processed successfully",
            "document_id": document_id,
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=ProcessingResponse)
async def process_query(request: QueryRequest):
    """Process a natural language query"""
    try:
        start_time = time.time()
        
        # Process the query
        service = get_query_service()
        result = await service.process_query(request)
        
        processing_time = time.time() - start_time
        result.processing_time = processing_time
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents", response_model=List[str])
async def list_documents():
    """List all processed documents"""
    try:
        service = get_document_service()
        return service.list_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the system"""
    try:
        service = get_document_service()
        await service.delete_document(document_id)
        return {"message": f"Document {document_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "LLM Document Processing System"}

@router.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        stats = {
            "total_documents": get_document_service().get_document_count(),
            "upload_directory": Config.UPLOAD_DIRECTORY,
            "vector_store_path": Config.CHROMA_PERSIST_DIRECTORY
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
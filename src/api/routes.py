from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
import os
import time
import uuid
from pathlib import Path

from src.core.models import QueryRequest, ProcessingResponse
from src.api.dependencies import get_document_service, get_query_service
from src.core.config import Config
from src.utils.logger import get_logger

from src.utils.cloud_sync import CloudSyncService

logger = get_logger(__name__)
router = APIRouter()

# Global dictionary to track progress of background indexing tasks
processing_tasks: Dict[str, Dict[str, Any]] = {}

async def process_document_background(document_id: str, file_path: str):
    """Background task to run heavy indexing steps"""
    try:
        service = get_document_service()
        await service.process_document(file_path, document_id=document_id)
        
        # Trigger background upload sync if configured
        try:
            CloudSyncService.upload_vector_store()
        except Exception as se:
            logger.error(f"Failed to sync vector store update to S3: {se}")

        processing_tasks[document_id] = {
            "status": "completed",
            "filename": processing_tasks[document_id]["filename"],
            "error": None
        }
        logger.info(f"Background indexing completed successfully for document {document_id}")
    except Exception as e:
        logger.error(f"Background indexing failed for document {document_id}: {e}", exc_info=True)
        processing_tasks[document_id] = {
            "status": "failed",
            "filename": processing_tasks[document_id]["filename"],
            "error": str(e)
        }

@router.post("/upload", response_model=dict)
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload and process a document in the background"""
    try:
        # Validate file type
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ['.pdf', '.docx', '.doc', '.eml', '.msg', '.txt', '.jpg', '.jpeg', '.png']:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Save uploaded file with unique name to prevent silent overwriting
        upload_path = Path(Config.UPLOAD_DIRECTORY)
        upload_path.mkdir(exist_ok=True)
        
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = upload_path / unique_filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            if len(content) > Config.MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="File too large")
            buffer.write(content)
            logger.info(f"Uploaded file {file.filename} (saved as {unique_filename}) size: {len(content)} bytes")
        
        # Initialize background task tracking
        document_id = str(uuid.uuid4())
        processing_tasks[document_id] = {
            "status": "processing",
            "filename": file.filename,
            "error": None
        }
        
        # Queue the indexing task
        background_tasks.add_task(process_document_background, document_id, str(file_path))
        
        return {
            "message": "Document upload accepted and indexing started in the background",
            "document_id": document_id,
            "filename": file.filename,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents", response_model=List[str])
async def list_documents():
    """List all processed documents"""
    try:
        service = get_document_service()
        return service.list_documents()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the system"""
    try:
        service = get_document_service()
        await service.delete_document(document_id)
        return {"message": f"Document {document_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}", exc_info=True)
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{document_id}", response_model=dict)
async def get_task_status(document_id: str):
    """Get the status of a background document indexing task"""
    task = processing_tasks.get(document_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task or document ID not found")
    return task
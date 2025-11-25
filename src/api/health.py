"""
Health check endpoints with dependency checks
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, Any
from datetime import datetime
import os

from core.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class HealthStatus(BaseModel):
    """Health status model"""
    status: str
    timestamp: str
    version: str
    dependencies: Dict[str, str]


class DetailedHealthStatus(BaseModel):
    """Detailed health status with dependency checks"""
    status: str
    timestamp: str
    version: str
    checks: Dict[str, Dict[str, Any]]


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "dependencies": {
            "gemini_api": "configured",
            "vector_store": "ready",
            "embedding_model": Config.EMBEDDING_MODEL
        }
    }


@router.get("/health/detailed", response_model=DetailedHealthStatus)
async def detailed_health_check():
    """Detailed health check with dependency verification"""
    checks = {}
    overall_status = "healthy"
    
    # Check Gemini API configuration
    try:
        if Config.GEMINI_API_KEY:
            checks["gemini_api"] = {
                "status": "configured",
                "model": Config.GEMINI_MODEL
            }
        else:
            checks["gemini_api"] = {
                "status": "not_configured",
                "error": "GEMINI_API_KEY not set"
            }
            overall_status = "degraded"
    except Exception as e:
        checks["gemini_api"] = {
            "status": "error",
            "error": str(e)
        }
        overall_status = "unhealthy"
    
    # Check vector store directory
    try:
        vector_store_path = Config.CHROMA_PERSIST_DIRECTORY
        if os.path.exists(vector_store_path):
            checks["vector_store"] = {
                "status": "ready",
                "path": vector_store_path
            }
        else:
            checks["vector_store"] = {
                "status": "not_initialized",
                "path": vector_store_path
            }
            overall_status = "degraded"
    except Exception as e:
        checks["vector_store"] = {
            "status": "error",
            "error": str(e)
        }
        overall_status = "unhealthy"
    
    # Check embedding model configuration
    try:
        checks["embedding_model"] = {
            "status": "configured",
            "model": Config.EMBEDDING_MODEL
        }
    except Exception as e:
        checks["embedding_model"] = {
            "status": "error",
            "error": str(e)
        }
        overall_status = "degraded"
    
    # Check file system
    try:
        upload_dir = Config.UPLOAD_DIRECTORY
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
        checks["file_system"] = {
            "status": "ready",
            "upload_directory": upload_dir
        }
    except Exception as e:
        checks["file_system"] = {
            "status": "error",
            "error": str(e)
        }
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "checks": checks
    }


@router.get("/readiness")
async def readiness_check():
    """Readiness probe for Kubernetes/Render"""
    # Check if critical dependencies are ready
    try:
        if not Config.GEMINI_API_KEY:
            raise HTTPException(status_code=503, detail="Gemini API not configured")
        
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/liveness")
async def liveness_check():
    """Liveness probe for Kubernetes/Render"""
    return {"status": "alive"}

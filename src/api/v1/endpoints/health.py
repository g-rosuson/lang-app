"""Health check endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from src.config import settings
from src.services.language_analysis import get_language_analysis_service
from src.services.logging.logging import get_logger

router = APIRouter(prefix="/health", tags=["health"])
logger = get_logger(__name__)

@router.get("/status")
async def health_status():
    """Detailed health status endpoint."""
    return {"status": settings.health_status}

@router.get("/ping")
async def health_ping():
    """Simple ping endpoint for load balancers."""
    return {"status": "ok"}


def get_pipeline():
    """Dependency to get the language analysis pipeline."""
    try:
        return get_language_analysis_service()
    except Exception as e:
        logger.error(f"Failed to get language analysis service: {e}")
        raise HTTPException(status_code=503, detail="Language analysis service not available")


@router.get("/language")
async def language_health(pipeline = Depends(get_pipeline)):
    """
    Health check for the language analysis pipeline.
    
    This endpoint provides information about:
    - Pipeline initialization status
    - Individual processor status
    - System resources
    """
    try:
        status = pipeline.get_pipeline_status()
        return {
            "status": "healthy" if status["initialized"] else "unhealthy",
            "pipeline": status
        }
    except Exception as e:
        logger.error(f"Failed to get pipeline status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get language pipeline status")


@router.get("/performance")
async def performance_metrics(pipeline = Depends(get_pipeline)):
    """
    Get comprehensive performance metrics and cache statistics.
    
    This endpoint provides detailed performance information including:
    - Processing times and statistics
    - Cache hit rates and performance
    - System resource usage
    - Recent request metrics
    """
    try:
        metrics = pipeline.get_performance_metrics()
        return {
            "status": "healthy",
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")
"""Language processing endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from src.config import settings
from src.services.language_analysis import get_language_analysis_service
from src.services.language_analysis.models import AnalysisRequest, AnalysisResult
from src.services.logging.logging import get_logger

router = APIRouter(prefix="/language", tags=["language"])
logger = get_logger(__name__)


def get_pipeline():
    """Dependency to get the language analysis pipeline."""
    try:
        return get_language_analysis_service()
    except Exception as e:
        logger.error(f"Failed to get language analysis service: {e}")
        raise HTTPException(status_code=503, detail="Language analysis service not available")


@router.get("/supported-languages")
async def get_supported_languages():
    """Get list of supported languages."""
    return {"languages": settings.supported_languages}


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_text(
    request: AnalysisRequest,
    pipeline = Depends(get_pipeline)
):
    """
    Analyze text for comprehensive language features.
    
    This endpoint provides comprehensive language analysis including:
    - Spell checking
    - Token analysis (SpaCy)
    - Advanced linguistic analysis (Stanza)
    - Basic text statistics
    """
    try:
        if not pipeline.is_initialized():
            raise HTTPException(
                status_code=503, 
                detail="Language analysis pipeline not initialized"
            )
        
        logger.info(f"Analyzing text: '{request.text[:50]}...'")
        result = pipeline.analyze(request)
        
        logger.info(f"Analysis completed successfully for {len(request.text)} characters")
        return result
        
    except ValueError as e:
        logger.warning(f"Text validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

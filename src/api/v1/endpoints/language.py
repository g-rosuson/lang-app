"""Language processing endpoints."""
from fastapi import APIRouter, HTTPException
from src.config import settings

router = APIRouter()

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages."""
    return {"languages": settings.supported_languages}

@router.post("/analyze")
async def analyze_text(text: str):
    """Analyze text for language features."""
    if not text or len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    return {
        "text": text,
        "word_count": len(text.split()),
        "character_count": len(text),
        "status": "analyzed"
    }
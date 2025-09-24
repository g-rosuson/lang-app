"""Health check endpoints."""
from fastapi import APIRouter
from src.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": settings.health_status}
"""Root endpoints."""
from fastapi import APIRouter
from src.config import settings

router = APIRouter()

@router.get("/")
async def root():
    """Get root endpoint."""
    return {"message": f"{settings.app_name} is running!"}
"""Main API router for v1 endpoints."""
from fastapi import APIRouter
from .endpoints import health, language

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(language.router, prefix="/language", tags=["language"])
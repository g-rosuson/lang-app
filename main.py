from fastapi import FastAPI
from src.api.v1.api import api_router
from src.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)

# Include all API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)
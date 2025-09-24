from fastapi import FastAPI
from src.api.v1.api import api_router

app = FastAPI(title="Language App", version="1.0.0")

# Include all API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Language App is running!"}

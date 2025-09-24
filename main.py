from fastapi import FastAPI

app = FastAPI(title="Language App", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Language App is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
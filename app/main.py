from fastapi import FastAPI
from app.api.routes import jobs

app = FastAPI(title="Asynchronous Image Description Service")

app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])

@app.get("/health")
async def health_check():
    """Health check endpoint to verify service is running."""
    return {"status": "healthy"} 
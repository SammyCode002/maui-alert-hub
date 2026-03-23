"""
Health check endpoint.

WHY have a health check?
When you deploy this to a server, the hosting platform (Railway, Render, etc.)
pings this endpoint to make sure your app is alive. If it stops responding,
they restart it automatically. Simple but essential.
"""

from datetime import datetime

from fastapi import APIRouter, Request

from app.services.limiter import limiter, GENERAL

router = APIRouter()


@router.get("/health")
@limiter.limit(GENERAL)
async def health_check(request: Request):
    """Returns the current status of the API."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0",
    }

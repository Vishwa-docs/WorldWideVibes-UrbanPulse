"""
Health-check router for UrbanPulse API.

Provides a lightweight endpoint that monitoring tools and the frontend
can poll to confirm the backend is alive.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Return basic service health information."""
    return {"status": "healthy", "version": "1.0.0"}

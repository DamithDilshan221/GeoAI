"""Health-check endpoint.

GET /api/v1/health  →  {"status": "ok", "app_env": "..."}

This intentionally does NOT check database connectivity yet — that
upgrade happens in Phase 4 once a DB connection pool exists.
"""

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    """Return a simple health status and the current app environment."""
    settings = get_settings()
    return {"status": "ok", "app_env": settings.APP_ENV}

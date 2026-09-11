"""GeoAI Backend — FastAPI application factory.

The `create_app()` function builds and configures the FastAPI instance.
Module-level `app = create_app()` so `uvicorn app.main:app` works directly.
The factory pattern matters for testing — Phase 18's test suite will need
to instantiate fresh app instances with different configurations.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import setup_logging

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Application factory — instantiate, configure, and return a FastAPI app."""
    settings = get_settings()

    setup_logging()

    application = FastAPI(
        title="GeoAI Facility Finder",
        description="Intelligent Facility Finder & Smart Navigation Recommendation System",
        version="0.1.0",
    )

    # CORS — origins parsed from comma-separated env var
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global exception handlers — maps OperationalError → 503 and any other
    # unhandled exception → 500, both with a consistent JSON envelope carrying
    # a per-request correlation ID.  Must be registered before routes are added
    # so the middleware runs on every request.  §22.1, §22.2.
    register_exception_handlers(application)

    # Versioned API routes
    application.include_router(v1_router, prefix="/api/v1")

    logger.info("GeoAI app created", extra={"app_env": settings.APP_ENV})
    return application


app = create_app()

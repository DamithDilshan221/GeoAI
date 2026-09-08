"""V1 API router — aggregates all versioned route modules."""

from fastapi import APIRouter

from app.api.v1.routes import categories, facilities, health, nearby, routes

router = APIRouter()

router.include_router(health.router)
router.include_router(categories.router)
router.include_router(nearby.router)
router.include_router(facilities.router)
router.include_router(routes.router)

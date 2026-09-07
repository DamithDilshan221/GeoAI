"""Health-check endpoint.

GET /api/v1/health  →  {"status": "ok", "app_env": "..."}
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db_session
from app.schemas.health import HealthRead

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthRead)
def health(session: Session = Depends(get_db_session)) -> HealthRead | JSONResponse:  # noqa: B008
    try:
        session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "unreachable"

    status_code = 200 if db_status == "connected" else 503
    payload = HealthRead(
        status="ok" if db_status == "connected" else "error",
        app_env=get_settings().APP_ENV,
        database=db_status,
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())

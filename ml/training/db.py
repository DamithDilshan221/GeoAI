"""Resolves DATABASE_URL via backend's own settings -- one source of truth,
no duplicated .env parsing (resolved decision #3)."""
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

_BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))


def get_engine() -> Engine:
    from app.core.config import get_settings

    return create_engine(get_settings().DATABASE_URL)

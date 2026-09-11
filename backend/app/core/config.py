"""Typed application settings loaded from environment variables.

Uses pydantic-settings to parse and validate configuration at import time.
A missing required variable (e.g. DATABASE_URL) raises a clear error
immediately rather than surfacing as a confusing failure on the first request.
"""

import functools

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings, populated from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=["../.env", ".env"],
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── General ──────────────────────────────────────────────
    APP_ENV: str = "development"

    # ── Database (required — no default) ─────────────────────
    DATABASE_URL: str
    DATABASE_URL_TEST: str = "postgresql+psycopg://postgres:changeme@localhost:5432/geoai_test"

    # ── CORS ─────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:5173"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins_list(self) -> list[str]:
        """Split the comma-separated CORS_ORIGINS string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # ── Google Maps ──────────────────────────────────────────
    GOOGLE_MAPS_API_KEY: str = ""

    # ── Search defaults ──────────────────────────────────────
    DEFAULT_SEARCH_RADIUS_M: int = 1000
    MAX_SEARCH_RADIUS_M: int = 10000

    # ── Pedestrian Routing ───────────────────────────────────────────────
    PEDESTRIAN_WALKING_SPEED_MPS: float = 1.2
    # Public OSRM demo endpoint (MVP); replace with self-hosted URL in production (§14.3).
    OSRM_BASE_URL: str = "https://router.project-osrm.org"

    # ── Recommendation engine ────────────────────────────────
    RECOMMENDATION_CONFIG_PATH: str = "config/recommendation_weights.yaml"
    STALENESS_HORIZON_HOURS: float = 24.0
    SUITABILITY_PENALTY_SCORE: float = 20.0

    # ── Historical Usage ─────────────────────────────────────
    USAGE_HISTORY_DAYS: int = 90


@functools.lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton Settings instance.

    The first call validates all env vars; subsequent calls return
    the same object without re-reading the environment.
    """
    return Settings()  # type: ignore[call-arg]

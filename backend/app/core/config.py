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

    # ── Recommendation engine ────────────────────────────────
    RECOMMENDATION_CONFIG_PATH: str = "config/recommendation_weights.yaml"


@functools.lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton Settings instance.

    The first call validates all env vars; subsequent calls return
    the same object without re-reading the environment.
    """
    return Settings()  # type: ignore[call-arg]

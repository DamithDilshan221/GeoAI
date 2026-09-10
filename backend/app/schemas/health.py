from typing import Literal

from pydantic import BaseModel


class HealthRead(BaseModel):
    status: Literal["ok", "error"]
    app_env: str
    database: Literal["connected", "unreachable"]
    prediction_provider: dict  # {"version": str, "algorithm": str | None}

"""Pydantic schemas for the pedestrian routing API."""

from typing import Literal

from pydantic import BaseModel

from app.domain.entities import RouteResult


class RouteResultRead(BaseModel):
    """Schema for a calculated route response."""

    distance_m: float
    estimated_time_s: int
    path: list[tuple[float, float]]
    source: Literal["network", "straight_line_estimate"]

    @classmethod
    def from_domain(cls, item: RouteResult) -> "RouteResultRead":
        return cls(
            distance_m=item.distance_m,
            estimated_time_s=item.estimated_time_s,
            path=item.path,
            source=item.source,
        )

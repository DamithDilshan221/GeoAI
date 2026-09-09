"""Coordinate validation logic."""

from app.domain.gis.exceptions import CoordinateValidationError


def validate_coordinates(*, lat: float, lon: float) -> None:
    """Validate that coordinates fall within acceptable geographic bounds.

    Raises CoordinateValidationError with ALL violations found.
    Bounds are INCLUSIVE: lat in [-90, 90], lon in [-180, 180].
    """
    errors = []

    if not -90.0 <= lat <= 90.0:
        errors.append(f"Latitude {lat} is out of bounds [-90, 90]")

    if not -180.0 <= lon <= 180.0:
        errors.append(f"Longitude {lon} is out of bounds [-180, 180]")

    if errors:
        raise CoordinateValidationError(errors)

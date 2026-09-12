from fastapi import HTTPException

from app.models.enums import AudienceType


def parse_audience(audience: str | None) -> AudienceType | None:
    if not audience:
        return None
    try:
        return AudienceType(audience.upper())
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid audience type") from None

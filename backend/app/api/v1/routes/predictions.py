from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.dependencies import get_ml_inference_service
from app.domain.exceptions import FacilityNotFoundError
from app.schemas.prediction import UsagePredictionRequest, UsagePredictionResponse
from app.services.ml_inference_service import MLInferenceService

router = APIRouter(tags=["Predictions"])


@router.post("/predictions/usage", response_model=UsagePredictionResponse)
def predict_usage(
    body: UsagePredictionRequest,
    service: MLInferenceService = Depends(get_ml_inference_service),  # noqa: B008
) -> UsagePredictionResponse:
    try:
        result = service.predict_usage(
            facility_id=body.facility_id,
            day_of_week=body.day_of_week,
            hour=body.hour,
            recent_usage=body.recent_usage,
        )
    except FacilityNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Facility {body.facility_id} not found"
        ) from None
    return UsagePredictionResponse(
        facility_id=body.facility_id,
        predicted_usage=result.predicted_usage,
        crowd_level=result.crowd_level,
        source=result.source,
        confidence=result.confidence,
    )

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

from app.models.enums import AudienceType


@dataclass(frozen=True)
class PredictionContext:
    facility_id: int
    category_id: int
    total_stalls: int
    audience: AudienceType
    day_of_week: int  # 0-6, Monday=0
    hour: int  # 0-23
    # category_code is used by TrainedModelUsageProvider (Phase 17).
    # Default "" keeps all pre-Phase-17 construction callsites valid;
    # HeuristicUsageProvider ignores it, exactly as it ignores recent_usage.
    category_code: str = ""
    recent_usage: float | None = None  # accepted, unused by heuristic


@dataclass(frozen=True)
class PredictionResult:
    predicted_usage: float
    crowd_level: Literal["LOW", "MEDIUM", "HIGH"]
    source: Literal["heuristic", "ml_model"]
    confidence: Literal["low", "medium", "high"]


class UsagePredictionProvider(ABC):
    @abstractmethod
    def predict(self, context: PredictionContext) -> PredictionResult:
        pass

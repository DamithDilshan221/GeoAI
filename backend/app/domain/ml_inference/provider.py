from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class PredictionContext:
    facility_id: int
    category_id: int
    capacity: int | None
    day_of_week: int          # 0-6, Monday=0
    hour: int                 # 0-23
    recent_usage: float | None = None   # accepted, unused by heuristic

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

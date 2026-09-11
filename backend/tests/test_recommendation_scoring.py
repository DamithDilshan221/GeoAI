"""Golden test for recommendation scoring — pure, no DB required.

Hand-verified expected values from the Phase 11 spec.  Each sub-score is
asserted individually so a weight bug cannot hide behind a coincidentally
correct final ranking.
"""

from datetime import datetime, timedelta

import pytest

from app.domain.entities import Facility
from app.domain.ml_inference.crowd_level import resolve_effective_capacity
from app.domain.recommendation.candidate import (
    RecommendationCandidate,
)
from app.domain.recommendation.explanation import build_explanation
from app.domain.recommendation.ranking import rank_candidates, score_candidate
from app.domain.recommendation.scoring import (
    crowd_score,
    distance_score,
    freshness_score,
    rating_score,
    suitability_score,
    travel_time_score,
)
from app.domain.recommendation.weights import RecommendationWeights
from app.models.enums import AudienceType, DataSource, FacilityStatus

# ── Shared fixtures ──────────────────────────────────────────────────────────

NOW = datetime(2026, 9, 10, 12, 0, 0)
WEIGHTS = RecommendationWeights(
    distance=0.15,
    travel_time=0.20,
    crowd=0.25,
    rating=0.15,
    freshness=0.15,
    suitability=0.10,
)
RADIUS_M = 1000
WALKING_SPEED_MPS = 1.2
STALENESS_HORIZON_HOURS = 24.0
SUITABILITY_PENALTY = 20.0


def _make_facility(
    fid: int = 1,
    total_stalls: int = 10,
    rating: float | None = 4.5,
    status_updated_at: datetime | None = None,
    audience: AudienceType = AudienceType.VISITOR,
) -> Facility:
    return Facility(
        id=fid,
        name=f"Facility-{fid}",
        category_id=1,
        latitude=0.0,
        longitude=0.0,
        status=FacilityStatus.OPEN,
        status_updated_at=status_updated_at or NOW,
        rating=rating,
        audience=audience,
        location_name=None,
        fixtures={},
        total_stalls=total_stalls,
        data_source=DataSource.SYNTHETIC,
        is_active=True,
        created_at=NOW,
        updated_at=NOW,
    )


def _make_candidate(
    facility: Facility,
    distance_m: float = 100.0,
    estimated_time_s: float = 100.0,
    travel_source: str = "network",
    predicted_usage: float = 2.0,
) -> RecommendationCandidate:
    return RecommendationCandidate(
        facility=facility,
        distance_m=distance_m,
        estimated_time_s=estimated_time_s,
        travel_source=travel_source,  # type: ignore[arg-type]
        predicted_usage=predicted_usage,
        prediction_source="heuristic",
    )


# ── Individual sub-score tests ───────────────────────────────────────────────


class TestDistanceScore:
    def test_close(self) -> None:
        assert distance_score(100, 1000) == pytest.approx(90.0)

    def test_far(self) -> None:
        assert distance_score(500, 1000) == pytest.approx(50.0)

    def test_at_boundary(self) -> None:
        assert distance_score(1000, 1000) == pytest.approx(0.0)

    def test_beyond_clamps_to_zero(self) -> None:
        assert distance_score(1500, 1000) == pytest.approx(0.0)


class TestTravelTimeScore:
    def test_fast(self) -> None:
        # max_acceptable = 1000/1.2 ≈ 833.33; 100/833.33 ≈ 0.12 → 88.0
        assert travel_time_score(100, 1000, 1.2) == pytest.approx(88.0, abs=0.05)

    def test_slow(self) -> None:
        assert travel_time_score(500, 1000, 1.2) == pytest.approx(40.0, abs=0.05)


class TestFreshnessScore:
    def test_recent(self) -> None:
        updated = NOW - timedelta(hours=1)
        assert freshness_score(updated, NOW, 24.0) == pytest.approx(95.83, abs=0.05)

    def test_stale(self) -> None:
        updated = NOW - timedelta(hours=20)
        assert freshness_score(updated, NOW, 24.0) == pytest.approx(16.67, abs=0.05)


class TestCrowdScore:
    def test_low_usage(self) -> None:
        assert crowd_score(2, 10) == pytest.approx(80.0)

    def test_high_usage(self) -> None:
        assert crowd_score(8, 10) == pytest.approx(20.0)

    def test_over_capacity_clamps(self) -> None:
        assert crowd_score(15, 10) == pytest.approx(0.0)


class TestRatingScore:
    def test_with_rating(self) -> None:
        assert rating_score(4.5) == pytest.approx(90.0)

    def test_none_default(self) -> None:
        assert rating_score(None) == pytest.approx(50.0)


class TestSuitabilityScore:
    def test_no_preference(self) -> None:
        assert suitability_score(AudienceType.VISITOR, None, 20.0) == 100.0

    def test_unrecognised_preference(self) -> None:
        assert suitability_score(AudienceType.VISITOR, "fast_lane", 20.0) == 100.0

    def test_staff_preferred_met_when_staff(self) -> None:
        assert suitability_score(AudienceType.STAFF, "staff_preferred", 20.0) == 100.0

    def test_staff_preferred_penalty_when_visitor(self) -> None:
        assert suitability_score(AudienceType.VISITOR, "staff_preferred", 20.0) == 20.0

    def test_wheelchair_is_noop(self) -> None:
        """wheelchair_accessible is documented as a legacy no-op in v3 — always 100."""
        assert suitability_score(AudienceType.VISITOR, "wheelchair_accessible", 20.0) == 100.0


# ── Golden A/B ranking test ──────────────────────────────────────────────────


class TestGoldenRanking:
    def test_candidate_a_vs_b(self) -> None:
        fac_a = _make_facility(
            fid=1,
            total_stalls=10,
            rating=4.5,
            status_updated_at=NOW - timedelta(hours=1),
        )
        fac_b = _make_facility(
            fid=2,
            total_stalls=10,
            rating=3.0,
            status_updated_at=NOW - timedelta(hours=20),
        )

        cand_a = _make_candidate(fac_a, distance_m=100, estimated_time_s=100, predicted_usage=2)
        cand_b = _make_candidate(fac_b, distance_m=500, estimated_time_s=500, predicted_usage=8)

        common = dict(
            radius_m=RADIUS_M,
            now=NOW,
            secondary_preference=None,
            weights=WEIGHTS,
            walking_speed_mps=WALKING_SPEED_MPS,
            staleness_horizon_hours=STALENESS_HORIZON_HOURS,
            suitability_penalty=SUITABILITY_PENALTY,
        )
        scored_a = score_candidate(cand_a, **common)
        scored_b = score_candidate(cand_b, **common)

        # Assert every individual sub-score for A
        assert scored_a.sub_scores["distance"] == pytest.approx(90.0, abs=0.05)
        assert scored_a.sub_scores["travel_time"] == pytest.approx(88.0, abs=0.05)
        assert scored_a.sub_scores["freshness"] == pytest.approx(95.83, abs=0.05)
        assert scored_a.sub_scores["crowd"] == pytest.approx(80.0, abs=0.05)
        assert scored_a.sub_scores["rating"] == pytest.approx(90.0, abs=0.05)
        assert scored_a.sub_scores["suitability"] == pytest.approx(100.0, abs=0.05)

        # Assert every individual sub-score for B
        assert scored_b.sub_scores["distance"] == pytest.approx(50.0, abs=0.05)
        assert scored_b.sub_scores["travel_time"] == pytest.approx(40.0, abs=0.05)
        assert scored_b.sub_scores["freshness"] == pytest.approx(16.67, abs=0.05)
        assert scored_b.sub_scores["crowd"] == pytest.approx(20.0, abs=0.05)
        assert scored_b.sub_scores["rating"] == pytest.approx(60.0, abs=0.05)
        assert scored_b.sub_scores["suitability"] == pytest.approx(100.0, abs=0.05)

        # Assert final scores
        assert scored_a.final_score == pytest.approx(88.97, abs=0.05)
        assert scored_b.final_score == pytest.approx(42.00, abs=0.05)

        # Assert ranking order
        ranked = rank_candidates([scored_b, scored_a])
        assert ranked[0].candidate.facility.id == 1  # A first
        assert ranked[1].candidate.facility.id == 2  # B second


class TestSuitabilityPenaltyDelta:
    """Candidate C is identical to A except staff_preferred is requested
    but facility is VISITOR → exact 8.0 delta (0.10 × (100 − 20))."""

    def test_exact_delta(self) -> None:
        fac_a = _make_facility(
            fid=1,
            total_stalls=10,
            rating=4.5,
            status_updated_at=NOW - timedelta(hours=1),
            audience=AudienceType.STAFF,
        )
        fac_c = _make_facility(
            fid=3,
            total_stalls=10,
            rating=4.5,
            status_updated_at=NOW - timedelta(hours=1),
            audience=AudienceType.VISITOR,
        )

        cand_a = _make_candidate(fac_a, distance_m=100, estimated_time_s=100, predicted_usage=2)
        cand_c = _make_candidate(fac_c, distance_m=100, estimated_time_s=100, predicted_usage=2)

        common_kwargs = dict(
            radius_m=RADIUS_M,
            now=NOW,
            secondary_preference="staff_preferred",
            weights=WEIGHTS,
            walking_speed_mps=WALKING_SPEED_MPS,
            staleness_horizon_hours=STALENESS_HORIZON_HOURS,
            suitability_penalty=SUITABILITY_PENALTY,
        )

        scored_a = score_candidate(cand_a, **common_kwargs)
        scored_c = score_candidate(cand_c, **common_kwargs)

        assert scored_a.sub_scores["suitability"] == 100.0
        assert scored_c.sub_scores["suitability"] == SUITABILITY_PENALTY

        delta = scored_a.final_score - scored_c.final_score
        assert delta == pytest.approx(8.0, abs=0.05)


# ── Explanation tests ────────────────────────────────────────────────────────


class TestBuildExplanation:
    def test_network_no_estimated(self) -> None:
        fac = _make_facility(status_updated_at=NOW - timedelta(hours=1), rating=4.5)
        cand = _make_candidate(fac, travel_source="network")
        scored = score_candidate(
            cand,
            radius_m=RADIUS_M,
            now=NOW,
            secondary_preference=None,
            weights=WEIGHTS,
            walking_speed_mps=WALKING_SPEED_MPS,
            staleness_horizon_hours=STALENESS_HORIZON_HOURS,
            suitability_penalty=SUITABILITY_PENALTY,
        )
        explanation = build_explanation(scored, WEIGHTS)
        assert "Recommended because" in explanation
        assert "estimated" not in explanation.lower()

    def test_straight_line_includes_estimated(self) -> None:
        fac = _make_facility(status_updated_at=NOW - timedelta(hours=1), rating=4.5)
        cand = _make_candidate(fac, travel_source="straight_line_estimate")
        scored = score_candidate(
            cand,
            radius_m=RADIUS_M,
            now=NOW,
            secondary_preference=None,
            weights=WEIGHTS,
            walking_speed_mps=WALKING_SPEED_MPS,
            staleness_horizon_hours=STALENESS_HORIZON_HOURS,
            suitability_penalty=SUITABILITY_PENALTY,
        )
        explanation = build_explanation(scored, WEIGHTS)
        assert "estimated" in explanation.lower()


# ── resolve_effective_capacity shared function ───────────────────────────────


class TestResolveEffectiveCapacity:
    def test_positive_stalls_used(self) -> None:
        assert resolve_effective_capacity(20) == 20.0

    def test_zero_stalls_uses_default(self) -> None:
        assert resolve_effective_capacity(0) == 10.0

    def test_custom_default(self) -> None:
        assert resolve_effective_capacity(0, default=15.0) == 15.0

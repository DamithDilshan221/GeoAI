"""Rule-based explanation builder for the top recommendation."""

from app.domain.recommendation.candidate import ScoredCandidate
from app.domain.recommendation.weights import RecommendationWeights

# Human-readable templates per factor.
_TEMPLATES: dict[str, str] = {
    "distance": "it is very close to your location",
    "travel_time": "a short walk away",
    "travel_time_estimated": "an estimated short walk away",
    "freshness": "its status was recently updated",
    "crowd": "it is expected to be less crowded",
    "rating": "it has a high user rating",
    "suitability": "it meets your accessibility preference",
}


def build_explanation(
    top: ScoredCandidate, weights: RecommendationWeights
) -> str:
    """Build a natural-language explanation naming the top 1-2 contributors.

    "Contributor" means weight × sub-score (weighted contribution),
    per decision #9.  When travel_time is a top contributor and the
    candidate's travel_source is ``"straight_line_estimate"``, the clause
    must include the word "estimated".
    """
    weight_map = {
        "distance": weights.distance,
        "travel_time": weights.travel_time,
        "freshness": weights.freshness,
        "crowd": weights.crowd,
        "rating": weights.rating,
        "suitability": weights.suitability,
    }

    contributions = {
        factor: weight_map[factor] * top.sub_scores[factor]
        for factor in weight_map
    }

    ranked = sorted(
        contributions.items(), key=lambda kv: kv[1], reverse=True
    )

    top_factors = [ranked[0]]
    if len(ranked) > 1 and ranked[1][1] > 0:
        top_factors.append(ranked[1])

    reasons: list[str] = []
    for factor, _ in top_factors:
        if factor == "travel_time":
            if top.candidate.travel_source == "straight_line_estimate":
                reasons.append(_TEMPLATES["travel_time_estimated"])
            else:
                reasons.append(_TEMPLATES["travel_time"])
        else:
            reasons.append(_TEMPLATES[factor])

    if len(reasons) == 1:
        return f"Recommended because {reasons[0]}."
    return f"Recommended because {reasons[0]}, and {reasons[1]}."

def resolve_effective_capacity(total_stalls: int, default: float = 10.0) -> float:
    """Shared capacity fallback: total_stalls (if > 0) -> hard default.
    Used by HeuristicUsageProvider (Phase 10). NOTE: RecommendationService's
    crowd sub-score (Phase 11) currently calls the OLD two-argument shape of
    this function and will fail until that phase's own correction updates its
    call site to match — this is expected and is that phase's job, not this one's."""
    return float(total_stalls) if total_stalls > 0 else default


def derive_crowd_level(predicted_usage: float, effective_capacity: float) -> str:
    """
    Implements the exact thresholds from the ML architecture doc §9.4.
    effective_capacity must be > 0 — the caller is responsible for resolving a real
    value before calling this; pass a sane positive fallback (e.g. 10) if even the
    category median is unavailable, never zero (division by zero).
    """
    ratio = predicted_usage / effective_capacity
    if ratio < 0.4:
        return "LOW"
    if ratio < 0.75:
        return "MEDIUM"
    return "HIGH"


def bucket_confidence(sample_count: int) -> str:
    """
    Tier-1-only confidence grading. Callers at Tier 2/3 do not call this — they
    hard-code 'low' directly, since sample count at those tiers doesn't change
    the confidence per §14.6's explicit instruction.
    """
    if sample_count >= 8:
        return "high"
    if sample_count >= 3:
        return "medium"
    raise ValueError(
        "bucket_confidence called on a sub-threshold sample count — "
        "the caller should have fallen through to Tier 2 instead"
    )

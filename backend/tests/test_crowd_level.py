import pytest

from app.domain.ml_inference.crowd_level import bucket_confidence, derive_crowd_level


def test_derive_crowd_level():
    # LOW < 0.4
    assert derive_crowd_level(3.9, 10.0) == "LOW"

    # MEDIUM 0.4 <= ratio < 0.75
    assert derive_crowd_level(4.0, 10.0) == "MEDIUM"
    assert derive_crowd_level(5.0, 10.0) == "MEDIUM"
    assert derive_crowd_level(7.4, 10.0) == "MEDIUM"

    # HIGH >= 0.75
    assert derive_crowd_level(7.5, 10.0) == "HIGH"
    assert derive_crowd_level(9.0, 10.0) == "HIGH"


def test_bucket_confidence():
    assert bucket_confidence(8) == "high"
    assert bucket_confidence(10) == "high"
    assert bucket_confidence(3) == "medium"
    assert bucket_confidence(7) == "medium"

    with pytest.raises(ValueError):
        bucket_confidence(2)

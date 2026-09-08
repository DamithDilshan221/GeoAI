import pytest

from app.domain.gis.coordinate_validation import CoordinateValidationError, validate_coordinates


def test_valid_coordinates():
    # Boundary and interior points
    validate_coordinates(lat=90.0, lon=180.0)
    validate_coordinates(lat=-90.0, lon=-180.0)
    validate_coordinates(lat=0.0, lon=0.0)
    validate_coordinates(lat=6.9271, lon=79.8612)  # Colombo


def test_invalid_latitude():
    with pytest.raises(CoordinateValidationError) as exc:
        validate_coordinates(lat=91.0, lon=0.0)
    assert "Latitude 91.0 is out of bounds" in str(exc.value)

    with pytest.raises(CoordinateValidationError) as exc:
        validate_coordinates(lat=-91.0, lon=0.0)
    assert "Latitude -91.0 is out of bounds" in str(exc.value)


def test_invalid_longitude():
    with pytest.raises(CoordinateValidationError) as exc:
        validate_coordinates(lat=0.0, lon=181.0)
    assert "Longitude 181.0 is out of bounds" in str(exc.value)

    with pytest.raises(CoordinateValidationError) as exc:
        validate_coordinates(lat=0.0, lon=-181.0)
    assert "Longitude -181.0 is out of bounds" in str(exc.value)


def test_both_invalid_aggregates_errors():
    with pytest.raises(CoordinateValidationError) as exc:
        validate_coordinates(lat=91.0, lon=181.0)
    
    error_msg = str(exc.value)
    assert "Latitude 91.0 is out of bounds" in error_msg
    assert "Longitude 181.0 is out of bounds" in error_msg
    assert len(exc.value.errors) == 2

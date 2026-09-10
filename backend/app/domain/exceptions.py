class DomainError(Exception):
    """Base exception for domain errors."""

    pass


class FacilityNotFoundError(DomainError):
    """Raised when a facility cannot be found."""

    pass

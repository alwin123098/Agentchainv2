"""Exception classes for SDK."""


class TrustLayerException(Exception):
    """Base exception for Trust Layer SDK."""
    pass


class AuthenticationError(TrustLayerException):
    """Raised when authentication fails."""
    pass


class VerificationError(TrustLayerException):
    """Raised when verification fails."""
    pass


class NetworkError(TrustLayerException):
    """Raised when network request fails."""
    pass


class RateLimitError(TrustLayerException):
    """Raised when rate limit is exceeded."""
    pass


class ValidationError(TrustLayerException):
    """Raised when input validation fails."""
    pass

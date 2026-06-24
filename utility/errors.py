"""Custom exceptions and helpers for the project."""
from typing import Optional


class BaseAppError(Exception):
    """Base class for application errors.

    Attributes:
        msg: human readable message
        code: optional machine-readable error code
    """

    def __init__(self, msg: str, code: Optional[str] = None):
        super().__init__(msg)
        self.msg = msg
        self.code = code

    def to_dict(self) -> dict:
        return {"error": {"message": self.msg, "code": self.code}}


class ValidationError(BaseAppError):
    """Raised when input validation fails."""


class NotFoundError(BaseAppError):
    """Raised when an expected resource is not found."""


class ExternalServiceError(BaseAppError):
    """Raised when an external service fails or returns an error."""


def wrap_exceptions(func):
    """Decorator that converts exceptions to BaseAppError, preserving context."""
    from functools import wraps

    @wraps(func)
    def _inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseAppError:
            raise
        except Exception as exc:
            raise ExternalServiceError(str(exc)) from exc

    return _inner

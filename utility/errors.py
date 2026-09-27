# custom error classes + decorator to wrap exceptions
from typing import Optional


class BaseAppError(Exception):
    def __init__(self, msg: str, code: Optional[str] = None):
        super().__init__(msg)
        self.msg = msg
        self.code = code

    def to_dict(self) -> dict:
        return {"error": {"message": self.msg, "code": self.code}}


class ValidationError(BaseAppError):
    pass


class NotFoundError(BaseAppError):
    pass


class ExternalServiceError(BaseAppError):
    pass


def wrap_exceptions(func):
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

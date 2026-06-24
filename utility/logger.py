"""Simple logging utility.

Provides:
 - get_logger(name): returns a configured logger
 - exception_handler: decorator that logs exceptions and re-raises or converts them
"""
import logging
import logging.handlers
import functools
import os
from typing import Callable

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

DEFAULT_LOG_FILE = os.path.join(LOG_DIR, "app.log")


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a configured logger with console and rotating file handlers."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)

    fmt = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    fh = logging.handlers.RotatingFileHandler(DEFAULT_LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # avoid propagation to root handlers twice
    logger.propagate = False
    return logger


def exception_handler(convert_exceptions: bool = False, logger_name: str = None) -> Callable:
    """Decorator to log exceptions raised in functions.

    If convert_exceptions is True, wraps exceptions in RuntimeError with context.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log = get_logger(logger_name or getattr(func, "__module__", __name__))
            try:
                return func(*args, **kwargs)
            except Exception as exc:  # log and optionally convert
                log.exception("Unhandled exception in %s: %s", func.__qualname__, exc)
                if convert_exceptions:
                    raise RuntimeError(f"Error in {func.__qualname__}: {exc}") from exc
                raise

        return wrapper

    return decorator

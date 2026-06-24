"""Utility package exports for logging and errors.

Use:
    from utility import logger, errors
    log = logger.get_logger(__name__)
    raise errors.ValidationError("bad input")
"""
# Import logger and errors modules from the current package

from . import logger, errors
# what this statement is doine 

__all__ = ["logger", "errors"]

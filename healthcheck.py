"""Healthcheck for container: verifies core modules import and a basic function call.

Exit code 0 means healthy; non-zero means unhealthy.
"""
import sys

try:
    # quick import checks
    import utility.logger as _logger
    import utility.errors as _errors
    # try creating a logger and calling a lightweight function
    l = _logger.get_logger("healthcheck")
    # call a tiny function to ensure module runtime is OK
    if not hasattr(_errors, "BaseAppError"):
        raise RuntimeError("errors module missing BaseAppError")
except Exception as e:
    print(f"unhealthy: {e}")
    sys.exit(1)

print("ok")
sys.exit(0)

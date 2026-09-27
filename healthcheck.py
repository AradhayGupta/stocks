# docker healthcheck, makes sure the utility modules import
import sys

try:
    import utility.logger as _logger
    import utility.errors as _errors
    l = _logger.get_logger("healthcheck")
    if not hasattr(_errors, "BaseAppError"):
        raise RuntimeError("errors module missing BaseAppError")
except Exception as e:
    print(f"unhealthy: {e}")
    sys.exit(1)

print("ok")
sys.exit(0)

"""Example control plane module demonstrating logger and error utilities.

This file is intentionally lightweight and meant to demonstrate usage. Replace
with your real control-plane logic as needed.
"""

from utility import logger, errors


log = logger.get_logger(__name__)


def validate_config(cfg: dict):
    if not isinstance(cfg, dict):
        raise errors.ValidationError("config must be a dict", code="INVALID_CONFIG")
    if "name" not in cfg:
        raise errors.ValidationError("missing 'name' in config", code="MISSING_FIELD")


@logger.exception_handler(convert_exceptions=False)
def run_control(cfg: dict):
    """Run a simple control flow that validates and logs output."""
    log.info("Starting control plane run")
    validate_config(cfg)
    name = cfg.get("name")
    log.info("Control plane running for %s", name)
    # simulate a step that could fail
    if cfg.get("fail_step"):
        raise RuntimeError("simulated failure in control step")
    log.info("Control plane completed successfully")


if __name__ == "__main__":
    # quick smoke test
    try:
        run_control({"name": "example", "fail_step": False})
    except Exception as e:
        log.error("Run failed: %s", e)

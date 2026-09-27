# basic control plane, validates config and logs the run
from utility import logger, errors


log = logger.get_logger(__name__)


def validate_config(cfg: dict):
    if not isinstance(cfg, dict):
        raise errors.ValidationError("config must be a dict", code="INVALID_CONFIG")
    if "name" not in cfg:
        raise errors.ValidationError("missing 'name' in config", code="MISSING_FIELD")


@logger.exception_handler(convert_exceptions=False)
def run_control(cfg: dict):
    log.info("Starting control plane run")
    validate_config(cfg)
    name = cfg.get("name")
    log.info("Control plane running for %s", name)
    if cfg.get("fail_step"):
        raise RuntimeError("simulated failure in control step")
    log.info("Control plane completed successfully")


if __name__ == "__main__":
    try:
        run_control({"name": "example", "fail_step": False})
    except Exception as e:
        log.error("Run failed: %s", e)

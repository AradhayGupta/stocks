# placeholder data fetch, just returns dummy data for now
from utility import logger, errors

log = logger.get_logger(__name__)


@logger.exception_handler(convert_exceptions=True)
def fetch_data(source: dict):
    if not source or "url" not in source:
        raise errors.ValidationError("source must contain 'url'")
    if source.get("bad"):
        raise ConnectionError("failed to connect to source")
    return {"data": [1, 2, 3], "source": source.get("url")}


if __name__ == "__main__":
    try:
        print(fetch_data({"url": "http://example.com"}))
    except Exception as e:
        log.error("data fetch failed: %s", e)

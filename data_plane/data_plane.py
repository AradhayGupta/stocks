"""Example data plane module demonstrating logger and error utilities.

This file shows how data-plane code can use the shared utilities.
"""

from utility import logger, errors

log = logger.get_logger(__name__)


@logger.exception_handler(convert_exceptions=True)
def fetch_data(source: dict):
    if not source or "url" not in source:
        raise errors.ValidationError("source must contain 'url'")
    # simulate fetching; in real code you'd use requests or aiohttp
    if source.get("bad"):
        raise ConnectionError("failed to connect to source")
    return {"data": [1, 2, 3], "source": source.get("url")}


if __name__ == "__main__":
    try:
        print(fetch_data({"url": "http://example.com"}))
    except Exception as e:
        log.error("data fetch failed: %s", e)

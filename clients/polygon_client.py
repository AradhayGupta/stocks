"""Polygon.io client moved to top-level clients package."""
import os
import requests
from typing import Dict, Any

BASE = "https://api.polygon.io"


def _get_api_key() -> str:
    key = os.environ.get("POLYGON_API_KEY")
    if not key:
        raise RuntimeError("POLYGON_API_KEY not set in environment")
    return key


def get_quote(ticker: str) -> Dict[str, Any]:
    api_key = _get_api_key()
    endpoint = f"{BASE}/v2/aggs/ticker/{ticker}/prev"
    params = {"apiKey": api_key}
    resp = requests.get(endpoint, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

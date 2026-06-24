"""Alpha Vantage client for fetching company overview/fundamentals."""
from dataclasses import dataclass
from typing import Optional, Any, Dict
import os


BASE = "https://www.alphavantage.co/query"


@dataclass
class Fundamentals:
    symbol: str
    pe_ratio: Optional[float]
    eps: Optional[float]
    week52_high: Optional[float]
    week52_low: Optional[float]
    market_cap: Optional[int]
    raw: Dict[str, Any]


def _get_api_key() -> str:
    key = os.environ.get("ALPHA_VANTAGE_KEY")
    if not key:
        raise RuntimeError("ALPHA_VANTAGE_KEY not set in environment")
    return key


def get_fundamentals(ticker: str, api_key: Optional[str] = None) -> Fundamentals:
    """Fetches the company overview from Alpha Vantage and returns a Fundamentals object.

    Fields parsed: PERatio, EPS, 52WeekHigh, 52WeekLow, MarketCapitalization.
    """
    # import requests lazily so the module can be imported in environments
    # where requests isn't installed (useful for lightweight syntax checks).
    import requests

    key = api_key or _get_api_key()
    params = {"function": "OVERVIEW", "symbol": ticker, "apikey": key}
    resp = requests.get(BASE, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    def _parse_float(k: str) -> Optional[float]:
        v = data.get(k)
        if v is None or v == "":
            return None
        try:
            return float(v)
        except Exception:
            return None

    def _parse_int(k: str) -> Optional[int]:
        v = data.get(k)
        if v is None or v == "":
            return None
        try:
            return int(float(v))
        except Exception:
            return None

    pe = _parse_float("PERatio")
    eps = _parse_float("EPS")
    high52 = _parse_float("52WeekHigh")
    low52 = _parse_float("52WeekLow")
    mcap = _parse_int("MarketCapitalization")

    return Fundamentals(symbol=ticker, pe_ratio=pe, eps=eps, week52_high=high52, week52_low=low52, market_cap=mcap, raw=data)

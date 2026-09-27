# polygon quotes and price history, saves latest quote to prices_cache
import os
import requests
from typing import Dict, Any

from db.connection import get_conn

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
    data = resp.json()

    results = data.get("results", [])
    if results:
        bar = results[0]
        price = bar.get("c")
        if price is not None:
            from datetime import datetime, timezone
            bar_ts = None
            if bar.get("t"):
                bar_ts = datetime.fromtimestamp(bar["t"] / 1000, tz=timezone.utc)
            conn = get_conn()
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO prices_cache
                                (ticker, price, open, high, low, vwap, volume, bar_ts, ts)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now())
                            ON CONFLICT (ticker) DO UPDATE SET
                                price  = EXCLUDED.price,
                                open   = EXCLUDED.open,
                                high   = EXCLUDED.high,
                                low    = EXCLUDED.low,
                                vwap   = EXCLUDED.vwap,
                                volume = EXCLUDED.volume,
                                bar_ts = EXCLUDED.bar_ts,
                                ts     = now()
                            """,
                            (
                                ticker.upper(), price,
                                bar.get("o"), bar.get("h"), bar.get("l"),
                                bar.get("vw"), bar.get("v") and int(bar["v"]),
                                bar_ts,
                            ),
                        )
            finally:
                conn.close()

    return data


def get_price_history(ticker: str, days: int = 90) -> Dict[str, Any]:
    from datetime import date, timedelta

    api_key = _get_api_key()
    end = date.today()
    start = end - timedelta(days=days)
    endpoint = f"{BASE}/v2/aggs/ticker/{ticker}/range/1/day/{start.isoformat()}/{end.isoformat()}"
    params = {"apiKey": api_key, "adjusted": "true", "sort": "asc"}
    resp = requests.get(endpoint, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

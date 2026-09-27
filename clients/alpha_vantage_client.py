# fundamentals (yfinance first, alpha vantage as backup) + alpha vantage news, cached in postgres
from dataclasses import dataclass
from typing import Optional, Any, Dict, List
import os

from db.connection import get_conn

BASE = "https://www.alphavantage.co/query"


@dataclass
class Fundamentals:
    symbol: str
    name: Optional[str]
    description: Optional[str]
    sector: Optional[str]
    industry: Optional[str]
    address: Optional[str]
    exchange: Optional[str]
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


def _check_rate_limit(data: dict):
    msg = data.get("Note") or data.get("Information")
    if msg:
        raise RuntimeError(f"Alpha Vantage API limit hit: {msg}")


def _read_fundamentals_cache(ticker: str, max_age_days: int) -> Optional[Fundamentals]:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT name, description, sector, industry, address, exchange,
                       pe_ratio, eps, week52_high, week52_low, market_cap
                FROM fundamentals_cache
                WHERE ticker = %s AND ts > now() - (%s * INTERVAL '1 day')
                """,
                (ticker, max_age_days),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return None

    (name, description, sector, industry, address, exchange,
     pe_ratio, eps, week52_high, week52_low, market_cap) = row
    return Fundamentals(
        symbol=ticker, name=name, description=description, sector=sector,
        industry=industry, address=address, exchange=exchange,
        pe_ratio=float(pe_ratio) if pe_ratio is not None else None,
        eps=float(eps) if eps is not None else None,
        week52_high=float(week52_high) if week52_high is not None else None,
        week52_low=float(week52_low) if week52_low is not None else None,
        market_cap=int(market_cap) if market_cap is not None else None,
        raw={},
    )


def _save_fundamentals_cache(ticker: str, result: Fundamentals):
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO fundamentals_cache
                        (ticker, name, description, sector, industry, address, exchange,
                         pe_ratio, eps, week52_high, week52_low, market_cap, ts)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, now())
                    ON CONFLICT (ticker) DO UPDATE SET
                        name        = EXCLUDED.name,
                        description = EXCLUDED.description,
                        sector      = EXCLUDED.sector,
                        industry    = EXCLUDED.industry,
                        address     = EXCLUDED.address,
                        exchange    = EXCLUDED.exchange,
                        pe_ratio    = EXCLUDED.pe_ratio,
                        eps         = EXCLUDED.eps,
                        week52_high = EXCLUDED.week52_high,
                        week52_low  = EXCLUDED.week52_low,
                        market_cap  = EXCLUDED.market_cap,
                        ts          = now()
                    """,
                    (
                        ticker, result.name, result.description,
                        result.sector, result.industry, result.address, result.exchange,
                        result.pe_ratio, result.eps, result.week52_high,
                        result.week52_low, result.market_cap,
                    ),
                )
    finally:
        conn.close()


def _fetch_fundamentals_alpha_vantage(ticker: str, api_key: Optional[str]) -> Fundamentals:
    import requests

    key = api_key or _get_api_key()
    params = {"function": "OVERVIEW", "symbol": ticker, "apikey": key}
    resp = requests.get(BASE, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    _check_rate_limit(data)

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

    return Fundamentals(
        symbol=ticker,
        name=data.get("Name") or None,
        description=data.get("Description") or None,
        sector=data.get("Sector") or None,
        industry=data.get("Industry") or None,
        address=data.get("Address") or None,
        exchange=data.get("Exchange") or None,
        pe_ratio=_parse_float("PERatio"),
        eps=_parse_float("EPS"),
        week52_high=_parse_float("52WeekHigh"),
        week52_low=_parse_float("52WeekLow"),
        market_cap=_parse_int("MarketCapitalization"),
        raw=data,
    )


def get_fundamentals(
    ticker: str, api_key: Optional[str] = None,
    max_age_days: int = 90, force_refresh: bool = False,
) -> Fundamentals:
    ticker = ticker.upper()

    if not force_refresh:
        cached = _read_fundamentals_cache(ticker, max_age_days)
        if cached:
            return cached

    try:
        from clients import yfinance_client
        result = yfinance_client.get_fundamentals(ticker)
    except Exception:
        result = _fetch_fundamentals_alpha_vantage(ticker, api_key)

    _save_fundamentals_cache(ticker, result)
    return result


def _read_news_cache(ticker: str, max_age_hours: int, limit: int) -> Optional[List[Dict[str, Any]]]:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT MAX(ts) FROM news_cache WHERE ticker = %s",
                (ticker,),
            )
            (latest,) = cur.fetchone()
            if latest is None:
                return None

            cur.execute(
                "SELECT now() - %s < (%s * INTERVAL '1 hour')",
                (latest, max_age_hours),
            )
            (is_fresh,) = cur.fetchone()
            if not is_fresh:
                return None

            cur.execute(
                """
                SELECT headline, sentiment, url, source
                FROM news_cache
                WHERE ticker = %s
                ORDER BY ts DESC
                LIMIT %s
                """,
                (ticker, limit),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    items = []
    for headline, sentiment, url, source in rows:
        items.append({
            "title": headline,
            "url": url,
            "source": source,
            "ticker_sentiment": [{
                "ticker": ticker,
                "ticker_sentiment_score": str(sentiment) if sentiment is not None else "0",
            }],
        })
    return items


def get_news(
    ticker: str, api_key: Optional[str] = None, limit: int = 10,
    max_age_hours: int = 6, force_refresh: bool = False,
) -> List[Dict[str, Any]]:
    ticker = ticker.upper()

    if not force_refresh:
        cached = _read_news_cache(ticker, max_age_hours, limit)
        if cached is not None:
            return cached

    import requests

    key = api_key or _get_api_key()
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": ticker,
        "limit": limit,
        "apikey": key,
    }
    resp = requests.get(BASE, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    _check_rate_limit(data)

    items = data.get("feed", [])
    if items:
        rows = []
        for item in items:
            headline = item.get("title", "")
            url = item.get("url")
            source = item.get("source")
            score = None
            for ts in item.get("ticker_sentiment", []):
                if ts.get("ticker", "").upper() == ticker:
                    try:
                        score = float(ts.get("ticker_sentiment_score", 0))
                    except (TypeError, ValueError):
                        score = None
                    break
            rows.append((ticker, headline, score, url, source))

        conn = get_conn()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.executemany(
                        "INSERT INTO news_cache (ticker, headline, sentiment, url, source) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        rows,
                    )
        finally:
            conn.close()

    return items

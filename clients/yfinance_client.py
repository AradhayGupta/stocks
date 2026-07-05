"""Yahoo Finance fallback client (unofficial, via yfinance).

Used only when Alpha Vantage's rate limit is hit. yfinance scrapes Yahoo's
internal endpoints rather than a published API, so it's less reliable
long-term — keep Alpha Vantage as the primary source.
"""
from clients.alpha_vantage_client import Fundamentals


def get_fundamentals(ticker: str) -> Fundamentals:
    import yfinance as yf

    info = yf.Ticker(ticker).info
    if not info or not (info.get("longName") or info.get("shortName")):
        raise RuntimeError(f"yfinance returned no data for {ticker}")

    address_parts = [info.get("address1"), info.get("city"), info.get("state"), info.get("country")]
    address = ", ".join(p for p in address_parts if p) or None

    return Fundamentals(
        symbol=ticker,
        name=info.get("longName") or info.get("shortName"),
        description=info.get("longBusinessSummary"),
        sector=info.get("sector"),
        industry=info.get("industry"),
        address=address,
        exchange=info.get("exchange"),
        pe_ratio=info.get("trailingPE"),
        eps=info.get("trailingEps"),
        week52_high=info.get("fiftyTwoWeekHigh"),
        week52_low=info.get("fiftyTwoWeekLow"),
        market_cap=info.get("marketCap"),
        raw=info,
    )

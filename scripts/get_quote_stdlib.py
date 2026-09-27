# polygon quote using only stdlib, no requests/dotenv needed
import os
import json
import sys
import urllib.request
from datetime import datetime


def load_env(path=".env"):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def get_quote_stdlib(ticker="SPCX", range_from: str = None, range_to: str = None):
    api_key = os.environ.get("POLYGON_API_KEY")
    if not api_key:
        raise RuntimeError("POLYGON_API_KEY not set in environment or .env")
    if range_from and range_to:
        url = (
            f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{range_from}/{range_to}?apiKey={api_key}"
        )
    else:
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?apiKey={api_key}"
    req = urllib.request.Request(url, headers={"User-Agent": "python-stdlib"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status != 200:
            body = resp.read().decode(errors="ignore")
            raise RuntimeError(f"HTTP {resp.status}: {body}")
        data = json.load(resp)
    return data


def pretty_print_single(resp, ticker="SPCX"):
    results = resp.get("results") or []
    if not results:
        print("No data returned for", ticker)
        return
    bar = results[0]
    ts = bar.get("t")
    if ts:
        ts = datetime.utcfromtimestamp(ts / 1000.0).isoformat() + "Z"
    print(f"Ticker: {ticker}")
    print(f"Time (UTC): {ts}")
    print(f"Open: {bar.get('o')}")
    print(f"High: {bar.get('h')}")
    print(f"Low: {bar.get('l')}")
    print(f"Close: {bar.get('c')}")
    print(f"VWAP: {bar.get('vw')}")
    print(f"Volume: {bar.get('v')}")
    print(f"N bars: {bar.get('n')}")


def pretty_print_range(resp, ticker="SPCX"):
    results = resp.get("results") or []
    if not results:
        print("No data returned for", ticker)
        return
    print(f"Ticker: {ticker} - {len(results)} bars")
    for i, bar in enumerate(results):
        ts = bar.get("t")
        if ts:
            ts = datetime.utcfromtimestamp(ts / 1000.0).isoformat() + "Z"
        print(f"[{i+1}/{len(results)}] Time: {ts} Open: {bar.get('o')} High: {bar.get('h')} Low: {bar.get('l')} Close: {bar.get('c')} VWAP: {bar.get('vw')} Volume: {bar.get('v')} N: {bar.get('n')}")


def _persist_price(ticker: str, resp: dict):
    results = resp.get("results") or []
    if not results:
        return
    bar = results[0]
    price = bar.get("c")
    if price is None:
        return
    try:
        from datetime import datetime, timezone
        from db.connection import get_conn
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
    except Exception as e:
        print(f"Warning: could not save price to DB: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fetch a ticker quote from Polygon.io")
    parser.add_argument("tickers", nargs="*", default=None, help="Ticker symbols (space-separated). If none provided, uses TICKER env or SPCX")
    parser.add_argument("--key", dest="key", help="Polygon API key (overrides .env)")
    parser.add_argument("--raw", dest="raw", action="store_true", help="Print raw JSON response")
    parser.add_argument("--from", dest="range_from", help="Start date for range query (YYYY-MM-DD)")
    parser.add_argument("--to", dest="range_to", help="End date for range query (YYYY-MM-DD)")
    args = parser.parse_args()

    load_env()
    if args.key:
        os.environ["POLYGON_API_KEY"] = args.key

    if args.tickers and len(args.tickers) > 0:
        tickers = args.tickers
    else:
        env_t = os.environ.get("TICKER")
        tickers = [env_t] if env_t else ["SPCX"]

    for ticker in tickers:
        try:
            resp = get_quote_stdlib(ticker, range_from=args.range_from, range_to=args.range_to)
            _persist_price(ticker, resp)
            if args.raw:
                print(f"== {ticker} ==")
                print(json.dumps(resp, indent=2))
            else:
                if args.range_from and args.range_to:
                    pretty_print_range(resp, ticker=ticker)
                else:
                    pretty_print_single(resp, ticker=ticker)
        except Exception as e:
            print(f"Error for {ticker}:", e)


if __name__ == "__main__":
    main()

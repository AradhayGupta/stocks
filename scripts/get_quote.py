"""Script to print AAPL quote using utility.polygon_client.get_quote

Usage: copy .env.example to .env and set POLYGON_API_KEY, then run:
    python scripts/get_quote.py
"""
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env if present

try:
    from clients.polygon_client import get_quote
except Exception:
    try:
        from control_plane.polygon_client import get_quote
    except Exception:
        try:
            from utility.polygon_client import get_quote
        except Exception:
            # last resort: import by path (legacy layout)
            import importlib.util
            import sys
            from pathlib import Path

            p = Path(__file__).resolve().parents[1] / "control_plane" / "polygon_client.py"
            spec = importlib.util.spec_from_file_location("polygon_client", str(p))
            mod = importlib.util.module_from_spec(spec)
            sys.modules["polygon_client"] = mod
            spec.loader.exec_module(mod)
            get_quote = mod.get_quote
from datetime import datetime


def main():
    ticker = "AAPL"
    try:
        resp = get_quote(ticker)
        # polygon /prev returns 'results' array with last aggregated bar(s)
        results = resp.get("results") or []
        if not results:
            print("No data returned for", ticker)
            return
        bar = results[0]
        # bar fields: o (open), c (close), h (high), l (low), v (volume), t (timestamp in ms)
        ts = bar.get("t")
        if ts:
            ts = datetime.utcfromtimestamp(ts / 1000.0).isoformat() + "Z"
        print(f"Ticker: {ticker}")
        print(f"Time (UTC): {ts}")
        print(f"Open: {bar.get('o')}")
        print(f"High: {bar.get('h')}")
        print(f"Low: {bar.get('l')}")
        print(f"Close: {bar.get('c')}")
        print(f"Volume: {bar.get('v')}")
    except Exception as e:
        print("Error fetching quote:", e)


if __name__ == "__main__":
    main()

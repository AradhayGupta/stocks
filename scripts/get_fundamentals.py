"""CLI to fetch fundamentals via Alpha Vantage.

Usage:
  python3 scripts/get_fundamentals.py AAPL --key YOURKEY
"""
import argparse
import os
import json
from clients.alpha_vantage_client import get_fundamentals


def main():
    p = argparse.ArgumentParser(description="Fetch company fundamentals from Alpha Vantage")
    p.add_argument("tickers", nargs="+", help="One or more ticker symbols")
    p.add_argument("--key", help="Alpha Vantage API key (optional, overrides ALPHA_VANTAGE_KEY env var)")
    p.add_argument("--raw", action="store_true", help="Print raw JSON response as well")
    args = p.parse_args()

    for t in args.tickers:
        try:
            f = get_fundamentals(t, api_key=args.key)
        except Exception as e:
            print(f"{t}: error: {e}")
            continue

        out = {
            "symbol": f.symbol,
            "pe_ratio": f.pe_ratio,
            "eps": f.eps,
            "52_week_high": f.week52_high,
            "52_week_low": f.week52_low,
            "market_cap": f.market_cap,
        }
        print(json.dumps(out))
        if args.raw:
            print(json.dumps(f.raw))


if __name__ == "__main__":
    main()

# cli for fundamentals. python3 scripts/get_fundamentals.py AAPL
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

        print(f"\n{'='*50}")
        print(f"{f.name} ({f.symbol})  —  {f.exchange}")
        print(f"Sector:   {f.sector}")
        print(f"Industry: {f.industry}")
        print(f"Address:  {f.address}")
        print(f"\n{f.description}")
        print(f"\nPE Ratio:    {f.pe_ratio}")
        print(f"EPS:         {f.eps}")
        print(f"52W High:    {f.week52_high}")
        print(f"52W Low:     {f.week52_low}")
        print(f"Market Cap:  {f.market_cap:,}" if f.market_cap else "Market Cap:  N/A")
        if args.raw:
            print(json.dumps(f.raw, indent=2))


if __name__ == "__main__":
    main()

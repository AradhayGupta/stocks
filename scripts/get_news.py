"""CLI to fetch news sentiment via Alpha Vantage.

Usage:
  python3 -m scripts.get_news AAPL
  python3 -m scripts.get_news AMD NVDA --limit 5
"""
import argparse
from clients.alpha_vantage_client import get_news


def sentiment_label(score):
    if score is None:
        return "  ?"
    if score >= 0.35:
        return f"+{score:.2f} BULLISH"
    if score <= -0.35:
        return f"{score:.2f} BEARISH"
    return f"{score:+.2f} neutral"


def main():
    p = argparse.ArgumentParser(description="Fetch news sentiment from Alpha Vantage")
    p.add_argument("tickers", nargs="+", help="One or more ticker symbols")
    p.add_argument("--limit", type=int, default=10, help="Number of articles to fetch (default 10)")
    args = p.parse_args()

    for ticker in args.tickers:
        try:
            items = get_news(ticker, limit=args.limit)
        except Exception as e:
            print(f"{ticker}: error: {e}")
            continue

        print(f"\n{'='*55}")
        print(f"  News & Sentiment: {ticker.upper()}  ({len(items)} articles)")
        print(f"{'='*55}")

        if not items:
            print("  No news found.")
            continue

        for item in items:
            score = None
            for ts in item.get("ticker_sentiment", []):
                if ts.get("ticker", "").upper() == ticker.upper():
                    try:
                        score = float(ts.get("ticker_sentiment_score", 0))
                    except (TypeError, ValueError):
                        score = None
                    break

            label = sentiment_label(score)
            headline = item.get("title", "")
            source = item.get("source", "")
            print(f"\n  [{label}]")
            print(f"  {headline}")
            print(f"  — {source}")

        print()


if __name__ == "__main__":
    main()

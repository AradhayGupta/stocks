-- Stock tracker schema

CREATE TABLE IF NOT EXISTS users (
    user_id    SERIAL PRIMARY KEY,
    email      TEXT NOT NULL UNIQUE,
    username   TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- One row per tax lot (a single purchase event)
CREATE TABLE IF NOT EXISTS holdings (
    lot_id     SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    ticker     TEXT NOT NULL,
    qty        NUMERIC(18, 6) NOT NULL CHECK (qty > 0),
    cost       NUMERIC(18, 4) NOT NULL CHECK (cost >= 0),  -- cost basis per share
    date       DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_holdings_user_ticker ON holdings(user_id, ticker);

-- Latest OHLCV bar per ticker from Polygon; upserted on each fetch
CREATE TABLE IF NOT EXISTS prices_cache (
    ticker  TEXT PRIMARY KEY,
    price   NUMERIC(18, 4) NOT NULL,  -- closing price
    open    NUMERIC(18, 4),
    high    NUMERIC(18, 4),
    low     NUMERIC(18, 4),
    vwap    NUMERIC(18, 4),
    volume  BIGINT,
    bar_ts  TIMESTAMPTZ,              -- timestamp of the bar from Polygon
    ts      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Company fundamentals from Alpha Vantage OVERVIEW; upserted on each fetch
CREATE TABLE IF NOT EXISTS fundamentals_cache (
    ticker      TEXT PRIMARY KEY,
    name        TEXT,
    description TEXT,
    sector      TEXT,
    industry    TEXT,
    address     TEXT,
    exchange    TEXT,
    pe_ratio    NUMERIC(10, 4),
    eps         NUMERIC(10, 4),
    week52_high NUMERIC(18, 4),
    week52_low  NUMERIC(18, 4),
    market_cap  BIGINT,
    ts          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- News items with optional sentiment score from Alpha Vantage
CREATE TABLE IF NOT EXISTS news_cache (
    id        SERIAL PRIMARY KEY,
    ticker    TEXT NOT NULL,
    headline  TEXT NOT NULL,
    sentiment REAL,    -- -1.0 (bearish) → 1.0 (bullish); NULL if not scored
    url       TEXT,
    source    TEXT,
    ts        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_news_cache_ticker_ts ON news_cache(ticker, ts DESC);

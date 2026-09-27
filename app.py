# streamlit app - search a ticker, shows price, chart, fundamentals and news
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv
import requests
import os
from datetime import datetime

load_dotenv()

from clients.polygon_client import get_quote, get_price_history
from clients.alpha_vantage_client import get_fundamentals, get_news

st.set_page_config(page_title="Stock Trader", layout="wide")
st.title("Stock Trader")


def refresh_history_for_range():
    ticker = st.session_state.get("ticker")
    if not ticker:
        return
    try:
        st.session_state.history = get_price_history(
            ticker, days=st.session_state.days
        )
        st.session_state.error = None
    except Exception as e:
        st.session_state.error = str(e)


col_input, col_days, col_btn = st.columns([4, 2, 1])
with col_input:
    ticker_input = st.text_input(
        "Ticker", placeholder="Enter ticker — e.g. AAPL, NVDA, AMD",
        label_visibility="collapsed"
    )
with col_days:
    days = st.selectbox(
        "Days", [30, 90, 180, 365], index=1,
        format_func=lambda d: f"Last {d} days",
        label_visibility="collapsed",
        key="days",
        on_change=refresh_history_for_range,
    )
with col_btn:
    fetch_btn = st.button("Fetch", use_container_width=True)


def get_top_news():
    api_key = os.getenv("POLYGON_API_KEY", "")
    try:
        r = requests.get(
            "https://api.polygon.io/v2/reference/news",
            params={"limit": 8, "order": "desc", "sort": "published_utc", "apiKey": api_key},
            timeout=8,
        )
        return r.json().get("results", [])
    except Exception:
        return []


if "top_news" not in st.session_state:
    st.session_state.top_news = get_top_news()

with st.sidebar:
    st.markdown("### 📰 Market Headlines")
    articles = st.session_state.top_news
    if articles:
        for article in articles:
            title    = article.get("title", "No title")
            pub      = article.get("publisher", {})
            source   = pub.get("name", "") if isinstance(pub, dict) else str(pub)
            if not source:
                source = article.get("author", "Unknown")
            url      = article.get("article_url") or article.get("url", "")
            summary  = article.get("description", "") or article.get("summary", "")
            time_pub = article.get("published_utc", "")
            try:
                dt = datetime.strptime(time_pub[:19], "%Y-%m-%dT%H:%M:%S")
                time_str = dt.strftime("%b %d · %H:%M")
            except Exception:
                time_str = ""
            snippet = summary[:120] + "…" if len(summary) > 120 else summary
            st.markdown(
                f"""
                <div style="padding:8px 0; border-bottom:1px solid #e2e8f0; margin-bottom:2px;">
                    <span style="font-size:0.68rem; color:#888; text-transform:uppercase;
                                 letter-spacing:0.04em;">{source} · {time_str}</span><br>
                    <a href="{url}" target="_blank" style="
                        font-size:0.82rem; font-weight:600; color:#0f172a;
                        text-decoration:none; line-height:1.4;">{title}</a>
                    <p style="color:#475569; font-size:0.75rem; margin:3px 0 0 0; line-height:1.4;">
                        {snippet}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.caption("No headlines available right now.")


if fetch_btn and ticker_input:
    ticker = ticker_input.strip().upper()
    st.session_state.ticker = ticker
    st.session_state.show_all_news = False

    with st.spinner(f"Fetching {ticker}..."):
        try:
            st.session_state.quote        = get_quote(ticker)
            st.session_state.fundamentals = get_fundamentals(ticker)
            st.session_state.news         = get_news(ticker, limit=20)
            st.session_state.history      = get_price_history(ticker, days=days)
            st.session_state.error        = None
        except Exception as e:
            st.session_state.error = str(e)

if st.session_state.get("error"):
    st.error(f"Error: {st.session_state.error}")

elif "quote" in st.session_state:
    ticker     = st.session_state.ticker
    quote      = st.session_state.quote
    f          = st.session_state.fundamentals
    news_items = st.session_state.news

    st.subheader(f"{f.name}  ({ticker})  —  {f.exchange}")
    st.caption(f"{f.sector}  |  {f.industry}  |  {f.address}")

    results = quote.get("results", [])
    if results:
        bar = results[0]
        st.divider()
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Close",  f"${bar.get('c', 0):,.2f}")
        c2.metric("Open",   f"${bar.get('o', 0):,.2f}")
        c3.metric("High",   f"${bar.get('h', 0):,.2f}")
        c4.metric("Low",    f"${bar.get('l', 0):,.2f}")
        c5.metric("Volume", f"{int(bar.get('v', 0)):,}")

    history = st.session_state.get("history", {})
    hist_results = history.get("results", [])
    if hist_results:
        df = pd.DataFrame(hist_results)
        df["date"] = pd.to_datetime(df["t"], unit="ms")
        for column in ("o", "h", "l", "c", "v"):
            df[column] = pd.to_numeric(df[column], errors="coerce")
        df = df.dropna(subset=["o", "h", "l", "c"])
        st.divider()
        st.subheader(f"Price History — Last {days} Days")
        chart_view = st.radio(
            "Chart view",
            ["Line", "Candlestick"],
            horizontal=True,
            label_visibility="collapsed",
            key="chart_view_2d",
        )

        if chart_view == "Line":
            figure = go.Figure(
                go.Scatter(
                    x=df["date"],
                    y=df["c"],
                    mode="lines",
                    line=dict(color="#287a68", width=2),
                    name=f"{ticker} Close",
                    hovertemplate="%{x|%b %d, %Y}<br>Close: $%{y:.2f}<extra></extra>",
                )
            )
            figure.update_layout(
                height=420,
                margin=dict(l=10, r=10, t=20, b=10),
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                xaxis_rangeslider_visible=True,
            )
        else:
            figure = go.Figure(
                go.Candlestick(
                    x=df["date"],
                    open=df["o"],
                    high=df["h"],
                    low=df["l"],
                    close=df["c"],
                    name=ticker,
                )
            )
            figure.update_layout(
                height=480,
                margin=dict(l=10, r=10, t=20, b=10),
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                xaxis_rangeslider_visible=True,
            )
        figure.update_layout(dragmode="pan")
        st.plotly_chart(figure, use_container_width=True)

    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PE Ratio", f.pe_ratio   if f.pe_ratio   else "N/A")
    c2.metric("EPS",      f.eps        if f.eps        else "N/A")
    c3.metric("52W High", f"${f.week52_high:,.2f}" if f.week52_high else "N/A")
    c4.metric("52W Low",  f"${f.week52_low:,.2f}"  if f.week52_low  else "N/A")

    if f.market_cap:
        st.caption(f"Market Cap:  ${f.market_cap:,}")
    if f.description:
        st.markdown("**Company Description**")
        st.write(f.description)

    st.divider()
    st.subheader("Recent News")

    def _score(item: dict) -> float:
        for ts in item.get("ticker_sentiment", []):
            if ts.get("ticker", "").upper() == ticker:
                try:
                    return float(ts.get("ticker_sentiment_score", 0))
                except (TypeError, ValueError):
                    return 0.0
        return 0.0

    def _label(score: float) -> str:
        if score >= 0.35:
            return f"🟢 +{score:.2f}  BULLISH"
        if score <= -0.35:
            return f"🔴 {score:.2f}  BEARISH"
        return f"⚪ {score:+.2f}  neutral"

    sorted_news  = sorted(news_items, key=lambda x: abs(_score(x)), reverse=True)
    show_all     = st.session_state.get("show_all_news", False)
    display_news = sorted_news if show_all else sorted_news[:5]

    for item in display_news:
        score    = _score(item)
        headline = item.get("title", "")
        source   = item.get("source", "")
        url      = item.get("url", "")
        st.markdown(f"**{_label(score)}** &nbsp;—&nbsp; *{source}*")
        st.markdown(f"[{headline}]({url})" if url else headline)
        st.divider()

    remaining = len(sorted_news) - 5
    if not show_all and remaining > 0:
        if st.button(f"Show {remaining} more articles"):
            st.session_state.show_all_news = True
            st.rerun()
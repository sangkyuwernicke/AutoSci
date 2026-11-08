"""Build the D1 (naive-transfer) / D5 (Korea-adapted) context strings per (name, date).

Pilot Spec: experiments/pilot/kospi-information-diet-vs-reasoning-scaffold.yaml

D1 = OHLCV/technical + English-gloss news + a generic earnings-calendar note
     ("just run TradingAgents on Korean tickers")
D5 = D1's technical layer + Korean-native news + DART disclosure summary +
     investor net-flow feature (foreign+institutional net buy, 20-day lookback)

Look-ahead guard: every input to build_d5_context is filtered to information
dated on or before the decision date (`date`), consistent with the idea's
'strict news/disclosure timestamp < decision time' backtest-realism rule.
"""

from __future__ import annotations

import pandas as pd

from korean_news_stub import NewsItem, news_as_of


def daily_returns(price_df: pd.DataFrame) -> pd.Series:
    return price_df["Close"].pct_change().dropna()


def technical_snapshot(
    price_df: pd.DataFrame, date: pd.Timestamp, sma_short: int, sma_long: int, rsi_period: int
) -> dict[str, float]:
    """Simple technical indicators computed using only data up to and including `date`."""
    window = price_df.loc[:date]
    close = window["Close"]

    delta = close.diff()
    gain = delta.clip(lower=0).rolling(rsi_period).mean()
    loss = (-delta.clip(upper=0)).rolling(rsi_period).mean()
    rs = gain / loss.replace(0, float("nan"))
    rsi = 100 - (100 / (1 + rs))

    return {
        "last_close": float(close.iloc[-1]),
        "sma_short": float(close.rolling(sma_short).mean().iloc[-1]),
        "sma_long": float(close.rolling(sma_long).mean().iloc[-1]),
        "rsi": float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0,
    }


def _tech_block(name: str, date: pd.Timestamp, tech: dict[str, float]) -> str:
    return (
        f"[Price/Technical — {name} on {date.date()}]\n"
        f"Last close: {tech['last_close']:.2f}\n"
        f"SMA(short): {tech['sma_short']:.2f}\n"
        f"SMA(long): {tech['sma_long']:.2f}\n"
        f"RSI: {tech['rsi']:.1f}\n"
    )


def build_d1_context(name: str, date: pd.Timestamp, tech: dict[str, float], news_items: list[NewsItem]) -> str:
    lines = [
        "[DIET: D1 — naive US-transfer diet]",
        _tech_block(name, date, tech),
        "[Machine-translated news, English gloss]",
    ]
    if news_items:
        for item in news_items:
            lines.append(f"- ({item.date}) {item.headline_en}")
    else:
        lines.append("(no news items in the lookback window)")
    lines.append(
        "[Earnings calendar note] Korean chaebol earnings typically cluster in Q1/Q3; "
        "no fine-grained per-filing detail is available in this naive diet."
    )
    return "\n".join(lines)


def _dart_block(filings_asof: list[dict]) -> str:
    if not filings_asof:
        return "(no substantive DART filings in the lookback window)"
    lines = []
    for filing in filings_asof[:5]:  # cap for prompt length
        snippet = filing.get("body_snippet") or "(body not fetched — title only)"
        lines.append(f"- ({filing['rcept_dt']}) {filing['report_nm']}\n  body: {snippet}")
    return "\n".join(lines)


def _flow_block(flow_df: pd.DataFrame | None, date: pd.Timestamp, lookback_days: int) -> str:
    if flow_df is None or flow_df.empty:
        return "(no investor-flow data available)"
    window = flow_df.loc[:date].tail(lookback_days)
    if window.empty:
        return "(no investor-flow data available as of this date)"
    foreign_col = "외국인합계" if "외국인합계" in window.columns else None
    inst_col = "기관합계" if "기관합계" in window.columns else None
    foreign_sum = float(window[foreign_col].sum()) if foreign_col else 0.0
    inst_sum = float(window[inst_col].sum()) if inst_col else 0.0
    return (
        f"Trailing {lookback_days}-trading-day net buy value (KRW):\n"
        f"  Foreign investors: {foreign_sum:,.0f}\n"
        f"  Institutional investors: {inst_sum:,.0f}\n"
        f"  Combined foreign+institutional: {foreign_sum + inst_sum:,.0f} "
        f"({'net buying' if (foreign_sum + inst_sum) > 0 else 'net selling'})"
    )


def build_d5_context(
    name: str,
    date: pd.Timestamp,
    tech: dict[str, float],
    news_items: list[NewsItem],
    dart_filings_asof: list[dict],
    flow_df: pd.DataFrame | None,
    flow_lookback_days: int,
) -> str:
    lines = [
        "[DIET: D5 — Korea-adapted diet]",
        _tech_block(name, date, tech),
        "[Korean-native news]",
    ]
    if news_items:
        for item in news_items:
            lines.append(f"- ({item.date}) {item.headline_kr}")
    else:
        lines.append("(뉴스 없음 / no news items in the lookback window)")
    lines.append("[DART disclosures]")
    lines.append(_dart_block(dart_filings_asof))
    lines.append("[Investor net-flow]")
    lines.append(_flow_block(flow_df, date, flow_lookback_days))
    return "\n".join(lines)


def build_context(
    diet: str,
    name_key: str,
    display_name: str,
    date: pd.Timestamp,
    price_df: pd.DataFrame,
    dart_filings_all: list[dict],
    flow_df: pd.DataFrame | None,
    cfg_windows: dict,
    dart_lookback_days: int,
    flow_lookback_days: int,
) -> str:
    tech = technical_snapshot(
        price_df, date, cfg_windows["technical_sma_short"], cfg_windows["technical_sma_long"], cfg_windows["technical_rsi_period"]
    )
    date_str = date.date().isoformat()
    news_items = news_as_of(name_key, date_str, lookback_days=10)

    if diet == "D1":
        return build_d1_context(display_name, date, tech, news_items)

    if diet == "D5":
        floor = date - pd.Timedelta(days=dart_lookback_days)
        dart_asof = [
            f for f in dart_filings_all if floor.date().isoformat() <= f["rcept_dt"] <= date_str
        ]
        return build_d5_context(display_name, date, tech, news_items, dart_asof, flow_df, flow_lookback_days)

    raise ValueError(f"unknown diet condition '{diet}'")

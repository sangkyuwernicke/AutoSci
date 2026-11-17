"""Build the D0 / D6a / D6b information-channel context strings for one (name, date).

Pilot Spec: experiments/pilot/global-linkage-channel-ablation-blanket-index.yaml

Timing note (pilot-level approximation): KOSPI and US markets trade on different
calendars/timezones. A KOSPI decision made at the close of Korean day D can only
see the most recently *completed* US session, which — because US markets close in
the early morning of Korean day D+1 relative to a US session dated D-1 — is the US
session dated strictly before D. We approximate this with `Series.asof(D - 1 day)`
on each US/cross-market return series, which is a conservative (slightly stale but
never look-ahead) proxy. The full study should replace this with exact session
timestamps.
"""

from __future__ import annotations

import pandas as pd


def daily_returns(price_df: pd.DataFrame) -> pd.Series:
    return price_df["Close"].pct_change().dropna()


def technical_snapshot(price_df: pd.DataFrame, date: pd.Timestamp, sma_short: int, sma_long: int, rsi_period: int) -> dict[str, float]:
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


def asof_return(returns: pd.Series, date: pd.Timestamp) -> float:
    """Most recently *known* daily return as of `date` (strictly before `date`)."""
    cutoff = date - pd.Timedelta(days=1)
    value = returns.asof(cutoff)
    return float(value) if pd.notna(value) else 0.0


def rolling_corr_asof(kospi_returns: pd.Series, foreign_returns: pd.Series, date: pd.Timestamp, lookback: int) -> float:
    """Rolling correlation between KOSPI's own returns and the as-of-aligned foreign returns."""
    trailing_dates = kospi_returns.loc[:date].tail(lookback).index
    if len(trailing_dates) < max(10, lookback // 3):
        return 0.0
    aligned_foreign = pd.Series(
        {d: asof_return(foreign_returns, d) for d in trailing_dates}
    )
    aligned_kospi = kospi_returns.loc[trailing_dates]
    corr = aligned_kospi.corr(aligned_foreign)
    return float(corr) if pd.notna(corr) else 0.0


def build_d0_context(name: str, date: pd.Timestamp, tech: dict[str, float]) -> str:
    return (
        f"[Price/Technical only — {name} on {date.date()}]\n"
        f"Last close: {tech['last_close']:.2f}\n"
        f"SMA(short): {tech['sma_short']:.2f}\n"
        f"SMA(long): {tech['sma_long']:.2f}\n"
        f"RSI: {tech['rsi']:.1f}\n"
    )


def build_d6a_context(
    date: pd.Timestamp,
    kospi_index_returns: pd.Series,
    nasdaq_returns: pd.Series,
    sox_returns: pd.Series,
    vix_returns: pd.Series,
    usdkrw_returns: pd.Series,
    lookback: int,
) -> str:
    corr = rolling_corr_asof(kospi_index_returns, nasdaq_returns, date, lookback)
    return (
        f"[Global-linkage channel D6a (blanket index correlation) — {date.date()}]\n"
        f"Rolling {lookback}-day KOSPI-index vs NASDAQ-100 correlation: {corr:.3f}\n"
        f"Latest known overnight NASDAQ-100 return: {asof_return(nasdaq_returns, date):+.2%}\n"
        f"Latest known overnight SOX (semiconductor index) return: {asof_return(sox_returns, date):+.2%}\n"
        f"Latest known VIX change: {asof_return(vix_returns, date):+.2%}\n"
        f"Latest known USD/KRW change: {asof_return(usdkrw_returns, date):+.2%}\n"
    )


def build_d6b_context(
    date: pd.Timestamp,
    samsung_returns: pd.Series,
    sk_hynix_returns: pd.Series,
    sox_returns: pd.Series,
    weight_samsung: float,
    weight_sk_hynix: float,
    lookback: int,
) -> str:
    corr_samsung = rolling_corr_asof(samsung_returns, sox_returns, date, lookback)
    corr_sk_hynix = rolling_corr_asof(sk_hynix_returns, sox_returns, date, lookback)
    r_mech = weight_samsung * corr_samsung + weight_sk_hynix * corr_sk_hynix
    return (
        f"[Global-linkage channel D6b (concentration-weighted mechanistic exposure) — {date.date()}]\n"
        f"Samsung Electronics vs SOX rolling {lookback}-day correlation: {corr_samsung:.3f}\n"
        f"SK Hynix vs SOX rolling {lookback}-day correlation: {corr_sk_hynix:.3f}\n"
        f"Cap-weighted mechanistic exposure signal r_mech = {r_mech:.3f} "
        f"(w_Samsung={weight_samsung}, w_SKHynix={weight_sk_hynix})\n"
        f"Latest known overnight SOX return: {asof_return(sox_returns, date):+.2%}\n"
    )

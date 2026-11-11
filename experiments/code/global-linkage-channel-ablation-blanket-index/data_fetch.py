"""Fetch and cache daily OHLCV data for the pilot universe and cross-market series.

Pilot Spec: experiments/pilot/global-linkage-channel-ablation-blanket-index.yaml
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass

import pandas as pd
import yfinance as yf


@dataclass(frozen=True)
class TickerSet:
    samsung: str
    sk_hynix: str
    kodex200: str
    kospi_index: str
    nasdaq100: str
    sox: str
    vix: str
    usdkrw: str

    def all_tickers(self) -> list[str]:
        return [
            self.samsung,
            self.sk_hynix,
            self.kodex200,
            self.kospi_index,
            self.nasdaq100,
            self.sox,
            self.vix,
            self.usdkrw,
        ]


def fetch_ticker_history(ticker: str, period: str, cache_dir: pathlib.Path) -> pd.DataFrame:
    """Fetch one ticker's daily OHLCV, using a local CSV cache if present."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    safe_name = ticker.replace("^", "IDX_").replace("=", "_")
    cache_path = cache_dir / f"{safe_name}.csv"

    if cache_path.exists():
        return pd.read_csv(cache_path, index_col=0, parse_dates=True)

    history = yf.Ticker(ticker).history(period=period)
    if history.empty:
        raise RuntimeError(f"yfinance returned no data for ticker '{ticker}'")

    history.index = history.index.tz_localize(None)
    history.to_csv(cache_path)
    return history


def fetch_all(tickers: TickerSet, period: str, cache_dir: pathlib.Path) -> dict[str, pd.DataFrame]:
    """Fetch OHLCV for every ticker in the pilot universe."""
    return {ticker: fetch_ticker_history(ticker, period, cache_dir) for ticker in tickers.all_tickers()}

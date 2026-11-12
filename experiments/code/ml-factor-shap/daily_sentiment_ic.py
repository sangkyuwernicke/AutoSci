#!/usr/bin/env python3
"""Daily news-sentiment test: rank IC and a daily long-short book, by year (focus: 2025).

  python daily_sentiment_ic.py --years 2020 2021 2022 2023 2024 2025 --out results/v17_daily_sentiment

Timing (BigKinds gives the publication DATE only, no time of day):
  news dated on a weekend / holiday is rolled to the next trading day s; news dated on a trading day stays on it.
  A  enter at the close of s          optimistic: articles published after the close of s are already "known"
  B  enter at the close of s + 1      conservative and tradable; the first-day reaction is not captured
Return = close[entry + h] / close[entry] - 1.  Both are reported; read B as what could have been traded.

Long-short: each signal day, long the top q and short the bottom q of that day's stocks with news (equal weight),
held h = 1 day; cost = `cost` x sum|dw| against the previous day's book (rebuilt from scratch after a gap).
Long-only: top q minus the equal-weight mean of the same day's stocks, same cost rule on the long book only.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from factor_ic import newey_west_t

TRADING_DAYS = 252
NW_LAG = 5


def to_trading_days(daily: pd.DataFrame, cal: pd.DatetimeIndex) -> pd.DataFrame:
    """Roll each ticker's daily sentiment to the first trading day >= its date (article-weighted mean)."""
    d = daily[["ticker", "date", "n_articles", "mean_score"]].copy()
    d["date"] = pd.to_datetime(d["date"]).dt.normalize()
    d = d[d["n_articles"] > 0]
    pos = cal.searchsorted(d["date"].to_numpy(), side="left")
    keep = pos < len(cal)                                    # news after the last trading day has no entry price
    d, pos = d[keep], pos[keep]
    d = d.assign(date=cal[pos], w=d["n_articles"] * d["mean_score"])
    g = d.groupby(["ticker", "date"], as_index=False).agg(n_articles=("n_articles", "sum"), w=("w", "sum"))
    g["mean_score"] = g["w"] / g["n_articles"]
    return g[["ticker", "date", "n_articles", "mean_score"]]


def forward_returns(close: pd.DataFrame, dates, horizon: int, entry_shift: int) -> pd.DataFrame:
    """[date x ticker] return from the close `entry_shift` trading days after the signal day's close, over `horizon`."""
    cal, dates = close.index, pd.DatetimeIndex(dates)
    pos = cal.searchsorted(dates, side="right") - 1          # last trading day <= date
    entry = pos + entry_shift
    exit_ = entry + horizon
    ok = (pos >= 0) & (exit_ < len(cal))
    v = close.to_numpy(float)
    out = np.full((len(dates), v.shape[1]), np.nan)
    out[ok] = v[exit_[ok]] / v[entry[ok]] - 1.0
    return pd.DataFrame(out, index=dates, columns=close.columns)


def attach_returns(sig: pd.DataFrame, close: pd.DataFrame, horizon: int, entry_shift: int) -> pd.DataFrame:
    dates = pd.DatetimeIndex(sorted(sig["date"].unique()))
    r = forward_returns(close, dates, horizon, entry_shift)
    ri, ci = r.index.get_indexer(sig["date"]), r.columns.get_indexer(sig["ticker"])
    vals = np.where((ri >= 0) & (ci >= 0), r.to_numpy()[ri.clip(0), ci.clip(0)], np.nan)
    return sig.assign(ret=vals)


def daily_ic(sig: pd.DataFrame, score: str = "mean_score", ret: str = "ret", min_n: int = 8) -> pd.Series:
    out = {}
    for d, g in sig.dropna(subset=[score, ret]).groupby("date"):
        if len(g) >= min_n and g[score].nunique() > 1 and g[ret].nunique() > 1:
            out[d] = spearmanr(g[score], g[ret])[0]
    return pd.Series(out, dtype=float).sort_index()


def quantile_backtest(sig: pd.DataFrame, cal: pd.DatetimeIndex, q: float = 0.2, min_n: int = 10,
                      cost: float = 0.002, step: int = 1) -> pd.DataFrame:
    """Long-short (+/-1/k) and long-only-excess books with turnover and cost, see module docstring.
    `step`: trading days between rebalances (1 = daily, 5 = weekly). A book is only carried over from the
    previous signal day when it was exactly `step` trading days earlier; otherwise it is rebuilt from scratch."""
    if not 0 < q < 0.5:
        raise ValueError("q must be in (0, 0.5)")
    pos = {d: i for i, d in enumerate(cal)}
    empty = pd.Series(dtype=float)
    prev_ls, prev_lo, prev_i, rows = empty, empty, None, []
    for d, g in sig.dropna(subset=["mean_score", "ret"]).groupby("date"):
        if len(g) < min_n:
            continue
        k = max(1, int(np.ceil(q * len(g))))
        g = g.sort_values(["mean_score", "ticker"], ascending=[False, True])
        top, bot = g.iloc[:k], g.iloc[-k:]
        w_lo = pd.Series(1.0 / k, index=top["ticker"].to_numpy())
        w_ls = pd.concat([w_lo, pd.Series(-1.0 / k, index=bot["ticker"].to_numpy())])
        adjacent = prev_i is not None and pos[d] == prev_i + step
        t_ls = w_ls.sub(prev_ls if adjacent else empty, fill_value=0.0).abs().sum()
        t_lo = w_lo.sub(prev_lo if adjacent else empty, fill_value=0.0).abs().sum()
        ls, lo = top["ret"].mean() - bot["ret"].mean(), top["ret"].mean() - g["ret"].mean()
        rows.append(dict(date=d, n=len(g), ls_gross=ls, lo_excess_gross=lo, ls_turnover=t_ls, lo_turnover=t_lo,
                         ls_net=ls - cost * t_ls, lo_net=lo - cost * t_lo))
        prev_ls, prev_lo, prev_i = w_ls, w_lo, pos[d]
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------------- data + report
def load_prices(path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    p = pd.read_parquet(path, columns=["date", "ticker", "close", "mcap", "market", "eligible"])
    p = p[(p["market"] == "KOSPI") & p["eligible"].eq(True)]
    p["date"] = pd.to_datetime(p["date"])
    close = p.pivot_table(index="date", columns="ticker", values="close", aggfunc="last").sort_index()
    mcap = p.pivot_table(index="date", columns="ticker", values="mcap", aggfunc="last").reindex(close.index)
    return close, mcap


def keep_top_n(sig: pd.DataFrame, mcap: pd.DataFrame, n: int) -> pd.DataFrame:
    """Point-in-time: keep tickers ranked within the top `n` by market cap on the signal day."""
    rank = mcap.rank(axis=1, ascending=False)
    ri, ci = rank.index.get_indexer(sig["date"]), rank.columns.get_indexer(sig["ticker"])
    r = np.where((ri >= 0) & (ci >= 0), rank.to_numpy()[ri.clip(0), ci.clip(0)], np.inf)
    return sig[r <= n]


def ic_row(ic: pd.Series, **meta) -> dict:
    return dict(**meta, n_days=len(ic), mean_ic=ic.mean(), t_nw=newey_west_t(ic, NW_LAG), hit_rate=(ic > 0).mean())


def ann_sharpe(x: pd.Series, periods: float = TRADING_DAYS) -> float:
    """Annualised Sharpe of a return series with `periods` observations per year (252 daily, 252/5 weekly)."""
    x = x.dropna()
    return float(x.mean() / x.std(ddof=1) * np.sqrt(periods)) if len(x) > 2 and x.std(ddof=1) > 0 else np.nan


def run_universe(name: str, sig: pd.DataFrame, close: pd.DataFrame, years, args) -> tuple[pd.DataFrame, pd.DataFrame]:
    ic_rows, bt_rows = [], []
    for shift, timing in ((0, "A same-day close"), (1, "B next-day close")):
        for h in args.horizons:
            s = attach_returns(sig, close, h, shift)
            for y in years:
                sy = s[s["date"].dt.year == y]
                ic = daily_ic(sy, min_n=args.min_n)
                if len(ic) > 2:
                    ic_rows.append(ic_row(ic, universe=name, timing=timing, horizon=h, year=y,
                                          avg_N=sy.groupby("date").size().mean()))
        s1 = attach_returns(sig, close, 1, shift)
        bt = quantile_backtest(s1, close.index, args.q, args.min_n, args.cost)
        for y in years:
            b = bt[bt["date"].dt.year == y]
            if len(b) > 2:
                bt_rows.append(dict(universe=name, timing=timing, year=y, n_days=len(b), avg_N=b["n"].mean(),
                                    ls_gross_bp_day=1e4 * b["ls_gross"].mean(), ls_turnover=b["ls_turnover"].mean(),
                                    ls_sharpe_gross=ann_sharpe(b["ls_gross"]), ls_sharpe_net=ann_sharpe(b["ls_net"]),
                                    breakeven_cost_bp=1e4 * b["ls_gross"].mean() / b["ls_turnover"].mean(),
                                    lo_excess_gross_bp_day=1e4 * b["lo_excess_gross"].mean(),
                                    lo_sharpe_net=ann_sharpe(b["lo_net"])))
    return pd.DataFrame(ic_rows), pd.DataFrame(bt_rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sentiment", default="data/real/sentiment_finbert.parquet")
    ap.add_argument("--prices", default="data/real/prices.parquet")
    ap.add_argument("--years", type=int, nargs="+", default=[2020, 2021, 2022, 2023, 2024, 2025])
    ap.add_argument("--horizons", type=int, nargs="+", default=[1, 5])
    ap.add_argument("--q", type=float, default=0.2)
    ap.add_argument("--min-n", type=int, default=10, help="min stocks with news on a day to use it")
    ap.add_argument("--cost", type=float, default=0.002)
    ap.add_argument("--top-n", type=int, default=200, help="second universe: top-N by market cap on the day")
    ap.add_argument("--out", default="results/v17_daily_sentiment")
    args = ap.parse_args()

    close, mcap = load_prices(args.prices)
    sig_all = to_trading_days(pd.read_parquet(args.sentiment), close.index)
    sig_all = sig_all[sig_all["ticker"].isin(close.columns)]
    universes = {"all KOSPI": sig_all, f"top{args.top_n} mcap": keep_top_n(sig_all, mcap, args.top_n)}
    ics, bts = zip(*(run_universe(n, s, close, args.years, args) for n, s in universes.items()))
    ic, bt = pd.concat(ics, ignore_index=True), pd.concat(bts, ignore_index=True)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    ic.to_csv(out / "daily_ic_by_year.csv", index=False, encoding="utf-8-sig")
    bt.to_csv(out / "daily_longshort_by_year.csv", index=False, encoding="utf-8-sig")
    fmt = lambda d: d.to_string(index=False, float_format=lambda v: f"{v:.3f}")                    # noqa: E731
    text = "\n".join(["# Daily FinBert sentiment", "", __doc__, "## Rank IC by year", fmt(ic), "",
                      "## Daily long-short / long-only by year", fmt(bt), ""])
    (out / "summary.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Weekly news-sentiment test: 5-trading-day signal, 5-trading-day hold, by year (focus: 2025).

  python weekly_sentiment_ic.py --years 2020 2021 2022 2023 2024 2025 --out results/v17_weekly_sentiment

Signal at rebalance day r: article-weighted mean FinBert score of the news rolled onto the last `window` (5)
trading days ending at r. Hold `horizon` (5) trading days; rebalance every 5th trading day.
Timing as in daily_sentiment_ic.py:  A enter at the close of r (optimistic: r's own articles may be after the close),
B enter at the close of r + 1 (conservative / tradable).
The weekday of the rebalance is arbitrary, so all five phases (offsets of the 5-day cycle) are run and averaged;
the spread across phases is reported as a robustness check.
Long-short / long-only books and costs are the same as in daily_sentiment_ic.py, with turnover measured from one
rebalance to the next (`step` = 5) and Sharpe annualised with 252/5 periods per year.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from daily_sentiment_ic import (TRADING_DAYS, ann_sharpe, attach_returns, daily_ic, keep_top_n, load_prices,
                                quantile_backtest, to_trading_days)
from factor_ic import newey_west_t

STEP = 5
NW_LAG_WEEKLY = 2


def rebalance_dates(cal: pd.DatetimeIndex, step: int = STEP, phase: int = 0) -> pd.DatetimeIndex:
    """Every `step`-th trading day starting at offset `phase`."""
    return cal[phase::step]


def trailing_signal(sig: pd.DataFrame, cal: pd.DatetimeIndex, window: int = STEP) -> pd.DataFrame:
    """Article-weighted mean score over the last `window` trading days ending at each day (that day included),
    for every (ticker, day) with at least one article in the window. Uses nothing dated after the day."""
    tickers = pd.Index(sorted(sig["ticker"].unique()))
    di, ti = cal.get_indexer(sig["date"]), tickers.get_indexer(sig["ticker"])
    n, s = np.zeros((len(cal), len(tickers))), np.zeros((len(cal), len(tickers)))
    np.add.at(n, (di, ti), sig["n_articles"].to_numpy(float))
    np.add.at(s, (di, ti), (sig["n_articles"] * sig["mean_score"]).to_numpy(float))
    zero = np.zeros((1, len(tickers)))
    cn, cs = np.vstack([zero, n.cumsum(axis=0)]), np.vstack([zero, s.cumsum(axis=0)])
    i = np.arange(len(cal))
    lo = np.maximum(i + 1 - window, 0)
    nw, sw = cn[i + 1] - cn[lo], cs[i + 1] - cs[lo]
    d_idx, t_idx = np.nonzero(nw > 0.5)
    return pd.DataFrame({"ticker": tickers[t_idx], "date": cal[d_idx], "n_articles": nw[d_idx, t_idx].round().astype(int),
                         "mean_score": sw[d_idx, t_idx] / nw[d_idx, t_idx]})


def study_phase(sig_all: pd.DataFrame, close: pd.DataFrame, years, phase: int, name: str, args) -> tuple[list, list]:
    cal = close.index
    reb = set(rebalance_dates(cal, STEP, phase))
    sig = trailing_signal(sig_all, cal, args.window)
    sig = sig[sig["date"].isin(reb)]
    ic_rows, bt_rows = [], []
    per_year = TRADING_DAYS / STEP
    for shift, timing in ((0, "A rebalance-day close"), (1, "B next-day close")):
        s = attach_returns(sig, close, args.horizon, shift)
        bt = quantile_backtest(s, cal, args.q, args.min_n, args.cost, step=STEP)
        for y in years:
            sy = s[s["date"].dt.year == y]
            ic = daily_ic(sy, min_n=args.min_n)
            if len(ic) > 4:
                ic_rows.append(dict(universe=name, timing=timing, year=y, phase=phase, n_weeks=len(ic),
                                    avg_N=sy.groupby("date").size().mean(), mean_ic=ic.mean(),
                                    t_nw=newey_west_t(ic, NW_LAG_WEEKLY), hit_rate=(ic > 0).mean()))
            b = bt[bt["date"].dt.year == y]
            if len(b) > 4:
                bt_rows.append(dict(universe=name, timing=timing, year=y, phase=phase, n_weeks=len(b), avg_N=b["n"].mean(),
                                    ls_gross_bp_wk=1e4 * b["ls_gross"].mean(), ls_turnover=b["ls_turnover"].mean(),
                                    ls_sharpe_gross=ann_sharpe(b["ls_gross"], per_year),
                                    ls_sharpe_net=ann_sharpe(b["ls_net"], per_year),
                                    breakeven_cost_bp=1e4 * b["ls_gross"].mean() / b["ls_turnover"].mean(),
                                    lo_excess_gross_bp_wk=1e4 * b["lo_excess_gross"].mean(),
                                    lo_sharpe_net=ann_sharpe(b["lo_net"], per_year)))
    return ic_rows, bt_rows


def average_over_phases(df: pd.DataFrame, spread_col: str) -> pd.DataFrame:
    keys = ["universe", "timing", "year"]
    g = df.drop(columns="phase").groupby(keys)
    out = g.mean().join(g[spread_col].agg(**{f"{spread_col}_min": "min", f"{spread_col}_max": "max"}))
    return out.reset_index()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sentiment", default="data/real/sentiment_finbert.parquet")
    ap.add_argument("--prices", default="data/real/prices.parquet")
    ap.add_argument("--years", type=int, nargs="+", default=[2020, 2021, 2022, 2023, 2024, 2025])
    ap.add_argument("--window", type=int, default=STEP, help="trailing trading days used for the signal")
    ap.add_argument("--horizon", type=int, default=STEP, help="holding period in trading days")
    ap.add_argument("--q", type=float, default=0.2)
    ap.add_argument("--min-n", type=int, default=20, help="min stocks with a signal on a rebalance day")
    ap.add_argument("--cost", type=float, default=0.002)
    ap.add_argument("--top-n", type=int, default=200)
    ap.add_argument("--out", default="results/v17_weekly_sentiment")
    args = ap.parse_args()

    close, mcap = load_prices(args.prices)
    sig_all = to_trading_days(pd.read_parquet(args.sentiment), close.index)
    sig_all = sig_all[sig_all["ticker"].isin(close.columns)]
    universes = {"all KOSPI": sig_all, f"top{args.top_n} mcap": keep_top_n(sig_all, mcap, args.top_n)}
    ic_rows, bt_rows = [], []
    for name, s in universes.items():
        for phase in range(STEP):
            a, b = study_phase(s, close, args.years, phase, name, args)
            ic_rows += a
            bt_rows += b
    ic = average_over_phases(pd.DataFrame(ic_rows), "mean_ic")
    bt = average_over_phases(pd.DataFrame(bt_rows), "ls_sharpe_net")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    ic.to_csv(out / "weekly_ic_by_year.csv", index=False, encoding="utf-8-sig")
    bt.to_csv(out / "weekly_longshort_by_year.csv", index=False, encoding="utf-8-sig")
    fmt = lambda d: d.to_string(index=False, float_format=lambda v: f"{v:.3f}")                    # noqa: E731
    text = "\n".join(["# Weekly FinBert sentiment", "", __doc__, "## Rank IC by year (mean over 5 phases)", fmt(ic), "",
                      "## Weekly long-short / long-only by year (mean over 5 phases)", fmt(bt), ""])
    (out / "summary.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

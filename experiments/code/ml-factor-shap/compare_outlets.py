#!/usr/bin/env python3
"""Compare KR-FinBert-SC news sentiment across outlets (매일경제 / 서울경제 / 한국경제) and their pool.

  python compare_outlets.py --panel 매일경제=data/news/sentiment_cmp/finbert/kospi_daily_sentiment.parquet \
      --panel 서울경제=data/news/outlets/서울경제/kospi_daily_sentiment.parquet \
      --panel 한국경제=data/news/outlets/한국경제/kospi_daily_sentiment.parquet --out results/v22_outlet_compare

Outputs (<out>/): coverage_by_year.csv, distribution.csv, pair_agreement.csv, ic_by_outlet.csv, summary.md.
  coverage   : ticker-days, tickers, articles per year
  distribution: ticker-day mean_score mean/std/quantiles and share positive/negative (|score| > 0.33)
  agreement  : on (ticker, date) pairs covered by both outlets: Pearson / Spearman / sign agreement
  ic         : daily rank IC of the ticker-day score vs forward returns (same code as daily_sentiment_ic.py;
               timing A = same-day close (optimistic), B = next-day close (tradable)), per outlet and for the pool
               (article-weighted mean over outlets). All KOSPI, 2020~2025 by default.
"""
from __future__ import annotations

import argparse
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

COLS = ["ticker", "date", "n_articles", "mean_score"]
POS_NEG = 0.33


def load(path: str) -> pd.DataFrame:
    d = pd.read_parquet(path)[COLS].copy()
    d["ticker"] = d["ticker"].astype(str).str.zfill(6)
    d["date"] = pd.to_datetime(d["date"]).dt.normalize()
    return d


def pool(panels: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Article-weighted mean score per (ticker, date) over all outlets."""
    d = pd.concat([p.assign(w=p["n_articles"] * p["mean_score"]) for p in panels.values()])
    g = d.groupby(["ticker", "date"], as_index=False).agg(n_articles=("n_articles", "sum"), w=("w", "sum"))
    g["mean_score"] = g["w"] / g["n_articles"]
    return g[COLS]


def pair_agreement(a: pd.DataFrame, b: pd.DataFrame) -> dict:
    m = a.merge(b, on=["ticker", "date"], suffixes=("_a", "_b"))
    if len(m) < 3:
        return dict(n_shared=len(m), pearson=np.nan, spearman=np.nan, sign_agree=np.nan)
    return dict(n_shared=len(m), pearson=float(m["mean_score_a"].corr(m["mean_score_b"])),
                spearman=float(spearmanr(m["mean_score_a"], m["mean_score_b"])[0]),
                sign_agree=float((np.sign(m["mean_score_a"]) == np.sign(m["mean_score_b"])).mean()))


def coverage(d: pd.DataFrame) -> pd.DataFrame:
    g = d.assign(year=d["date"].dt.year).groupby("year")
    return g.agg(ticker_days=("ticker", "size"), tickers=("ticker", "nunique"),
                 n_articles=("n_articles", "sum")).reset_index()


def distribution(d: pd.DataFrame) -> dict:
    s = d["mean_score"]
    return dict(ticker_days=len(d), mean=s.mean(), std=s.std(), q10=s.quantile(.1), q50=s.median(),
                q90=s.quantile(.9), share_pos=(s > POS_NEG).mean(), share_neg=(s < -POS_NEG).mean(),
                articles_per_ticker_day=d["n_articles"].mean())


def ic_table(panels: dict[str, pd.DataFrame], prices: str, years: list[int], min_n: int) -> pd.DataFrame:
    import daily_sentiment_ic as dsi
    close, _ = dsi.load_prices(prices)
    rows = []
    for name, p in panels.items():
        sig = dsi.to_trading_days(p, close.index)
        sig = sig[sig["ticker"].isin(close.columns)]
        for shift, timing in ((0, "A same-day close"), (1, "B next-day close")):
            for h in (1, 5):
                s = dsi.attach_returns(sig, close, h, shift)
                s = s[s["date"].dt.year.isin(years)]
                for y in years + ["all"]:
                    sy = s if y == "all" else s[s["date"].dt.year == y]
                    ic = dsi.daily_ic(sy, min_n=min_n)
                    if len(ic) > 2:
                        rows.append(dsi.ic_row(ic, outlet=name, timing=timing, horizon=h, year=y,
                                               avg_N=sy.groupby("date").size().mean()))
    return pd.DataFrame(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--panel", action="append", required=True, metavar="NAME=PARQUET")
    ap.add_argument("--prices", default="data/real/prices.parquet")
    ap.add_argument("--years", type=int, nargs="+", default=[2020, 2021, 2022, 2023, 2024, 2025])
    ap.add_argument("--min-n", type=int, default=10)
    ap.add_argument("--out", default="results/v22_outlet_compare")
    args = ap.parse_args()

    panels = {k: load(v) for k, v in (s.split("=", 1) for s in args.panel)}
    allp = {**panels, "pooled": pool(panels)}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cov = pd.concat([coverage(p).assign(outlet=k) for k, p in allp.items()])
    dist = pd.DataFrame({k: distribution(p) for k, p in allp.items()}).T
    agree = pd.DataFrame([dict(a=a, b=b, **pair_agreement(panels[a], panels[b])) for a, b in combinations(panels, 2)])
    ic = ic_table(allp, args.prices, args.years, args.min_n)
    cov.to_csv(out / "coverage_by_year.csv", index=False, encoding="utf-8-sig")
    dist.to_csv(out / "distribution.csv", encoding="utf-8-sig")
    agree.to_csv(out / "pair_agreement.csv", index=False, encoding="utf-8-sig")
    ic.to_csv(out / "ic_by_outlet.csv", index=False, encoding="utf-8-sig")
    fmt = lambda d, **k: d.to_string(float_format=lambda v: f"{v:.3f}", **k)                         # noqa: E731
    text = "\n".join(["# Outlet comparison (KR-FinBert-SC)", "", "## Coverage by year (ticker-days)",
                      fmt(cov.pivot(index="year", columns="outlet", values="ticker_days")), "",
                      "## Ticker-day score distribution", fmt(dist), "",
                      "## Pairwise agreement on shared (ticker, date)", fmt(agree, index=False), "",
                      "## Daily rank IC (2020~2025 pooled)", fmt(ic[ic["year"] == "all"], index=False), "",
                      "## Daily rank IC by year, timing B, horizon 1",
                      fmt(ic[(ic["timing"] == "B next-day close") & (ic["horizon"] == 1) & (ic["year"] != "all")]
                          .pivot(index="year", columns="outlet", values="mean_ic")), ""])
    (out / "summary.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Daily KR-FinBert-SC sentiment panel (build_news_sentiment_panel.py --method model --out-dir <in>/finbert)
-> input of data_real.build_panel.

  python prepare_sentiment.py --in-dir data/news/sentiment_cmp --out data/real
  -> data/real/sentiment_finbert.parquet

Each output has one row per (ticker, date) that had KOSPI-stock news: ticker, date, n_articles, mean_score.
Run the experiment with  python run_experiment.py --data real --raw-dir data/real --sentiment finbert
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from config import SENTIMENT_SOURCES

COLS = ["ticker", "date", "n_articles", "mean_score"]


def convert(src: Path) -> pd.DataFrame:
    d = pd.read_parquet(src)
    missing = set(COLS) - set(d.columns)
    if missing:
        raise ValueError(f"{src}: missing columns {sorted(missing)}")
    d = d[COLS].copy()
    d["ticker"] = d["ticker"].astype(str).str.zfill(6)
    d["date"] = pd.to_datetime(d["date"]).dt.normalize()
    d["n_articles"] = d["n_articles"].astype("int64")
    if d.duplicated(["ticker", "date"]).any():
        raise ValueError(f"{src}: duplicate (ticker, date) rows")
    if not d["mean_score"].between(-1.0, 1.0).all():
        raise ValueError(f"{src}: mean_score outside [-1, 1]")
    return d.sort_values(["ticker", "date"]).reset_index(drop=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in-dir", default="data/news/sentiment_cmp")
    ap.add_argument("--out", default="data/real")
    ap.add_argument("--sources", nargs="+", default=SENTIMENT_SOURCES, choices=SENTIMENT_SOURCES)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for s in args.sources:
        src = Path(args.in_dir) / s / "kospi_daily_sentiment.parquet"
        if not src.exists():
            print(f"[skip] {src} not found", file=sys.stderr)
            continue
        d = convert(src)
        d.to_parquet(out / f"sentiment_{s}.parquet", index=False)
        print(f"{s}: {len(d):,} ticker-days, {d.ticker.nunique()} tickers, "
              f"{d.date.min():%Y-%m-%d}~{d.date.max():%Y-%m-%d} -> {out}/sentiment_{s}.parquet")
    return 0


if __name__ == "__main__":
    sys.exit(main())

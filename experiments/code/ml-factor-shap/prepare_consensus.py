"""Normalise a vendor consensus export (FnGuide / DataGuide / Quantiwise, Refinitiv, ...) into
consensus.parquet for data_real.build_panel.

Why a vendor file: free sources (e.g. Naver Finance) only show the *current* consensus, so a historical
backtest built from them would silently use today's estimates for past dates (look-ahead). You need a
point-in-time history: one row per (ticker, snapshot date, target fiscal year).

Input CSV columns (map yours with --map old=new):
    ticker, snapshot_date, target_year, ni_est, sales_est      (values in `--unit` KRW, default 1e6 = million won)
Usage:
    python prepare_consensus.py consensus_export.csv --out data/real/consensus.parquet --unit 1e6
"""
import argparse

import numpy as np
import pandas as pd


def prepare(df, unit=1e6):
    for c in ("ticker", "snapshot_date", "target_year"):
        assert c in df.columns, f"missing column {c}"
    df = df.copy()
    df["ticker"] = df["ticker"].astype(str).str.replace(r"^A", "", regex=True).str.zfill(6)
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
    df["target_year"] = df["target_year"].astype(int)
    parts = []
    for col, metric in (("ni_est", "ni"), ("sales_est", "sales")):
        if col in df.columns:
            parts.append(df[["ticker", "snapshot_date", "target_year"]].assign(
                metric=metric, value=pd.to_numeric(df[col], errors="coerce") * unit))
    out = pd.concat(parts).dropna(subset=["value"])
    # checks
    stale = out[out.target_year < out.snapshot_date.dt.year]
    if len(stale):
        print(f"dropping {len(stale)} rows whose target year is already over at the snapshot date")
        out = out.drop(stale.index)
    dup = out.duplicated(["ticker", "snapshot_date", "target_year", "metric"]).sum()
    if dup:
        print(f"{dup} duplicate keys; keeping the last")
        out = out.drop_duplicates(["ticker", "snapshot_date", "target_year", "metric"], keep="last")
    cover = out.groupby(out.snapshot_date.dt.year)["ticker"].nunique()
    print("tickers with estimates per snapshot year:\n" + cover.to_string())
    return out.reset_index(drop=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--out", default="data/real/consensus.parquet")
    ap.add_argument("--unit", type=float, default=1e6)
    ap.add_argument("--map", nargs="*", default=[], help="old=new column renames")
    a = ap.parse_args()
    d = pd.read_csv(a.csv, dtype={"ticker": str}).rename(columns=dict(m.split("=") for m in a.map))
    prepare(d, a.unit).to_parquet(a.out)

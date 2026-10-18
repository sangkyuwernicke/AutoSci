"""Turn files downloaded by hand from KRX Data Marketplace into the inputs of data_real.build_panel.

    data/krx/snapshots/*.csv     month-end "all stocks" quotes (one file per date, or several dates per file)
        기준일자,종목코드,종목명,시장구분,종가,대비,등락률,시가,고가,저가,거래량,거래대금,시가총액,상장주식수
    data/krx/index_kospi.csv     일자,종가      (index_kosdaq.csv optional)

    python prepare_krx.py --krx-dir data/krx --out data/real

writes  prices_monthly.parquet  and  index.parquet.

Only month-end snapshots exist, so there is no daily series: VOL_20D cannot be built and DIST_52W_HIGH is
approximated from the last 12 month-end closes. Snapshot closes are not split-adjusted; see `monthly_returns`.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from universe import classify

COLS = {"기준일자": "date", "종목코드": "ticker", "종목명": "name", "시장구분": "market", "종가": "close",
        "시가총액": "mcap", "상장주식수": "shares"}
MARKETS = ("KOSPI", "KOSDAQ")


def read_csv_any(path, **kw):
    """KRX downloads are usually cp949; also accept utf-8 (with or without BOM)."""
    for enc in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            return pd.read_csv(path, encoding=enc, **kw)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"cannot decode {path}")


def load_snapshots(snap_dir):
    files = sorted(Path(snap_dir).rglob("*.csv"))
    if not files:
        raise FileNotFoundError(f"no csv files under {snap_dir}")
    frames = []
    for f in files:
        d = read_csv_any(f, dtype={"종목코드": str, "기준일자": str})
        d.columns = [c.strip() for c in d.columns]
        missing = [c for c in COLS if c not in d.columns]
        if missing:
            raise ValueError(f"{f.name}: missing columns {missing}; found {list(d.columns)}")
        frames.append(d[list(COLS)].rename(columns=COLS))
    s = pd.concat(frames, ignore_index=True)
    s["date"] = pd.to_datetime(s["date"].str.replace(r"\D", "", regex=True), format="%Y%m%d")
    s["ticker"] = s["ticker"].str.strip().str.zfill(6)
    for c in ("close", "mcap", "shares"):
        s[c] = pd.to_numeric(s[c].astype(str).str.replace(",", ""), errors="coerce")
    s["market"] = s["market"].str.strip().str.upper()
    dup = s.duplicated(["date", "ticker"]).sum()
    if dup:
        print(f"[krx] dropping {dup} duplicate date/ticker rows")
        s = s.drop_duplicates(["date", "ticker"], keep="last")
    return s


def is_common_stock(ticker):
    """Korean common shares have a code ending in 0; preferred shares end in 5, 7, K, ..."""
    return ticker[-1] == "0"


def monthly_returns(g):
    """One ticker, sorted by month. 1-month return from consecutive month-end snapshots.

    Raw closes jump at splits / reverse splits / stock dividends. When the share count moves by more than 10 %
    while market cap stays within [0.75, 1.33] of last month, the move is treated as a share-count event and the
    return is the market-cap change (= price return on adjusted prices). Otherwise it is the plain price return.
    Cash dividends are not included (price return). Returns across a missing month are NaN and start a new segment.
    """
    g = g.sort_values("date").copy()
    prev_ok = (g["date"].dt.year * 12 + g["date"].dt.month).diff() == 1
    price_ratio = g["close"] / g["close"].shift(1)
    mcap_ratio = g["mcap"] / g["mcap"].shift(1)
    shares_ratio = g["shares"] / g["shares"].shift(1)
    share_event = ((shares_ratio - 1).abs() > 0.10) & mcap_ratio.between(0.75, 1.33)
    ratio = np.where(share_event, mcap_ratio, price_ratio)
    g["ret1"] = np.where(prev_ok, ratio - 1, np.nan)
    g["seg"] = (~prev_ok).cumsum()
    g["adj_close"] = (1 + g["ret1"].fillna(0)).groupby(g["seg"]).cumprod() * 100
    g["share_event"] = share_event & prev_ok
    return g


def build_monthly(snaps):
    s = snaps[snaps["market"].isin(MARKETS)].copy()
    s["date"] = s["date"] + pd.offsets.MonthEnd(0)             # month-end label, as in data_real
    s = s.sort_values(["date", "ticker"]).drop_duplicates(["date", "ticker"], keep="last")
    flags = {t: classify(t, n) for t, n in s.drop_duplicates("ticker").set_index("ticker")["name"].items()}
    s["eligible"] = [is_common_stock(t) and not (flags[t][0] or flags[t][1]) for t in s["ticker"]]
    s = s[(s["close"] > 0) & (s["mcap"] > 0)]
    out = pd.concat([monthly_returns(g) for _, g in s.groupby("ticker")], ignore_index=True)
    n_ev = int(out["share_event"].sum())
    print(f"[krx] {len(out):,} stock-months, {out['ticker'].nunique():,} tickers, "
          f"{out['date'].min():%Y-%m} .. {out['date'].max():%Y-%m}; share-count events adjusted: {n_ev}")
    cnt = out.groupby("date")["ticker"].nunique()
    print(f"[krx] stocks per month: min {cnt.min()}, median {int(cnt.median())}, max {cnt.max()}; "
          f"eligible (common, non-financial, non-SPAC): {int(out.groupby('date')['eligible'].sum().median())} median")
    months = pd.date_range(out["date"].min(), out["date"].max(), freq="ME")
    gaps = months.difference(pd.DatetimeIndex(out["date"].unique()))
    if len(gaps):
        print(f"[krx] WARNING months with no snapshot: {[f'{d:%Y-%m}' for d in gaps]}")
    return out.drop(columns=["share_event"])


def load_index(krx_dir):
    frames = []
    for market in MARKETS:
        f = Path(krx_dir) / f"index_{market.lower()}.csv"
        if not f.exists():
            continue
        d = read_csv_any(f)
        d.columns = [c.strip() for c in d.columns]
        d = d.rename(columns={"일자": "date", "종가": "close"})[["date", "close"]]
        d["date"] = pd.to_datetime(d["date"])
        d["close"] = pd.to_numeric(d["close"].astype(str).str.replace(",", ""), errors="coerce")
        frames.append(d.assign(market=market))
    if not frames:
        raise FileNotFoundError(f"no index_kospi.csv / index_kosdaq.csv in {krx_dir}")
    return pd.concat(frames, ignore_index=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--krx-dir", default="data/krx")
    ap.add_argument("--out", default="data/real")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    build_monthly(load_snapshots(Path(a.krx_dir) / "snapshots")).to_parquet(out / "prices_monthly.parquet")
    idx = load_index(a.krx_dir)
    idx.to_parquet(out / "index.parquet")
    print(f"[krx] index: {', '.join(sorted(idx['market'].unique()))}, {idx['date'].min():%Y-%m-%d} .. {idx['date'].max():%Y-%m-%d}")


if __name__ == "__main__":
    main()

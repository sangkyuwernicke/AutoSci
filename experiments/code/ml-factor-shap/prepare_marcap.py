"""Build the price inputs of data_real.build_panel from the marcap dataset (daily KRX quotes since 1995).

    git clone https://github.com/FinanceData/marcap.git data/marcap     # once; `git pull` to update
    python prepare_marcap.py --marcap-dir data/marcap/data --out data/real --start 2013-01-01

writes
  prices.parquet  daily: date, ticker, close, mcap (KRW), market, eligible, volume
                  `close` is an *adjusted* index level (100 at first observation), chained from KRX's own daily
                  return `ChangesRatio`, which KRX computes against a base price already adjusted for splits,
                  mergers and similar events (e.g. Samsung Electronics 2018-05-04: -2.08 %, not -98 %).
                  Price returns only (no dividends). Because the series is daily, VOL_20D and a true 252-day
                  DIST_52W_HIGH become available.
  index.parquet   daily: date, market, close. A market-cap-weighted (previous-day cap) price index built from the
                  same data for KOSPI and KOSDAQ, so the benchmark covers the full sample. It is a proxy, not
                  the official index.

Eligibility on each date (all known on that date, so no look-ahead): KOSPI / KOSDAQ only (KONEX excluded),
common stock (code ends in 0), not a financial or SPAC by name, and `Dept` not one of SPAC, administrative issue,
investment-caution (환기), foreign company.
Stocks that disappear have no delisting return, which biases results slightly upward (same as before).
"""
import argparse
from pathlib import Path

import pandas as pd

from universe import classify

COLUMNS = ["Date", "Code", "Name", "Close", "ChangesRatio", "Volume", "Marcap", "Market", "Dept"]
MARKET_MAP = {"KOSPI": "KOSPI", "KOSDAQ": "KOSDAQ", "KOSDAQ GLOBAL": "KOSDAQ"}
EXCLUDED_DEPT_HINTS = ("SPAC", "관리종목", "투자주의환기", "외국기업")


def load_marcap(data_dir, start, end=None):
    """Read the yearly parquet files that overlap [start, end] and keep KOSPI / KOSDAQ rows in that range."""
    start, end = pd.Timestamp(start), (pd.Timestamp(end) if end else None)
    files = sorted(Path(data_dir).glob("marcap-*.parquet"))
    if not files:
        raise FileNotFoundError(f"no marcap-*.parquet under {data_dir}")
    frames = []
    for f in files:
        year = int(f.stem.split("-")[1])
        if year < start.year or (end is not None and year > end.year):
            continue
        d = pd.read_parquet(f, columns=COLUMNS)
        frames.append(d[d["Market"].isin(MARKET_MAP)])
    m = pd.concat(frames, ignore_index=True)
    m["Date"] = pd.to_datetime(m["Date"])
    m = m[m["Date"] >= start]
    return m if end is None else m[m["Date"] <= end]


def build_prices(m):
    m = m.rename(columns={"Date": "date", "Code": "ticker", "Name": "name", "Volume": "volume",
                          "Marcap": "mcap", "Market": "market", "Dept": "dept"}).copy()
    m["market"] = m["market"].map(MARKET_MAP)
    m["ticker"] = m["ticker"].astype(str).str.zfill(6)
    m = m.drop_duplicates(["date", "ticker"], keep="last").sort_values(["ticker", "date"])
    m = m[(m["Close"] > 0) & (m["mcap"] > 0)]

    m["ret"] = m["ChangesRatio"] / 100.0
    m["close"] = 100.0 * (1.0 + m["ret"].fillna(0.0)).groupby(m["ticker"]).cumprod()

    last_name = m.drop_duplicates("ticker", keep="last").set_index("ticker")["name"]
    flags = {t: classify(t, n) for t, n in last_name.items()}
    by_name = m["ticker"].map(lambda t: not (flags[t][0] or flags[t][1]))
    by_dept = ~m["dept"].fillna("").astype(str).str.contains("|".join(EXCLUDED_DEPT_HINTS), regex=True)
    m["eligible"] = (m["ticker"].str[-1] == "0") & by_name & by_dept
    return m


def build_index(m):
    """Cap-weighted (previous-day market cap) daily price index per market from KRX's own daily returns."""
    w = m.groupby("ticker")["mcap"].shift(1)
    ok = m["ret"].notna() & w.notna()
    x = pd.DataFrame({"date": m.loc[ok, "date"], "market": m.loc[ok, "market"],
                      "w": w[ok], "wr": m.loc[ok, "ret"] * w[ok]})
    g = x.groupby(["date", "market"])
    r = (g["wr"].sum() / g["w"].sum()).rename("r").reset_index().sort_values(["market", "date"])
    r["close"] = 1000.0 * (1.0 + r["r"]).groupby(r["market"]).cumprod()
    return r[["date", "market", "close"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--marcap-dir", default="data/marcap/data")
    ap.add_argument("--out", default="data/real")
    ap.add_argument("--start", default="2013-01-01",
                    help="first date to load (needs ~12 months before the first sample month)")
    ap.add_argument("--end", default=None)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    raw = load_marcap(a.marcap_dir, a.start, a.end)
    last = raw["Date"].max()
    if a.end is None and last < last + pd.offsets.MonthEnd(0) - pd.Timedelta(days=4):
        # The final month is still in progress: its "next-month return" would be a partial-month number.
        cut = last - pd.offsets.MonthBegin(1) - pd.Timedelta(days=1) if last.day != 1 else last
        raw = raw[raw["Date"] <= cut]
        print(f"[marcap] last month incomplete (data ends {last:%Y-%m-%d}); trimmed to {cut:%Y-%m-%d}")
    m = build_prices(raw)
    m[["date", "ticker", "close", "mcap", "market", "eligible", "volume"]].to_parquet(out / "prices.parquet")
    idx = build_index(m)
    idx.to_parquet(out / "index.parquet")

    n = m.groupby("date")["ticker"].nunique()
    el = m[m["eligible"]].groupby("date")["ticker"].nunique()
    print(f"[marcap] {len(m):,} stock-days, {m['ticker'].nunique():,} tickers, "
          f"{m['date'].min():%Y-%m-%d} .. {m['date'].max():%Y-%m-%d}")
    print(f"[marcap] stocks/day: median {int(n.median())}; eligible (common, non-financial, non-SPAC, "
          f"not flagged): median {int(el.median())}")
    print(f"[marcap] index: {', '.join(sorted(idx['market'].unique()))}, cap-weighted proxy "
          f"{idx['date'].min():%Y-%m-%d} .. {idx['date'].max():%Y-%m-%d}")
    print("[marcap] a prices.parquet in the same directory takes precedence over prices_monthly.parquet")


if __name__ == "__main__":
    main()

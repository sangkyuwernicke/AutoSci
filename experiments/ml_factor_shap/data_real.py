"""Build the (date, ticker) factor panel from raw KOSPI/KOSDAQ files with look-ahead control.

Expected files in `raw_dir` (produce them with fetch_real_data.py or your own source):

prices.parquet        daily: date, ticker, close (split/dividend-adjusted), mcap (KRW), market
                      ("KOSPI"/"KOSDAQ"), eligible (bool; False for financials, SPACs and
                      administrative / investment-caution issues *on that date*)
fundamentals.parquet  one row per ticker x quarter: ticker, period_end, filing_date,
                      quarterly STAND-ALONE flows  sales, gross_profit, op_income, net_income, cfo,
                      interest_expense, depreciation (optional)
                      and period-end stocks  equity, assets, liabilities, current_assets,
                      current_liabilities, inventory, cash, debt
macro.parquet         long: name, avail_date, value  for the five MACRO series (CPI_YOY and
                      TERM_SPREAD already derived; avail_date = date the figure became public)
index.parquet         optional daily: date, market, close  (benchmark blend, weighted by market cap)

Look-ahead rules: a fundamentals row is usable from `filing_date` on, never from `period_end`;
macro at month t uses only figures public by the end of month t-1.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from config import ALL_FEATURES, MACRO

FLOWS = ["sales", "gross_profit", "op_income", "net_income", "cfo", "interest_expense", "depreciation"]
STOCKS = ["equity", "assets", "liabilities", "current_assets", "current_liabilities",
          "inventory", "cash", "debt"]
MAX_STALENESS_MONTHS = 18


def _fundamental_factors(f):
    f = f.sort_values(["ticker", "period_end"]).copy()
    if "depreciation" not in f:
        f["depreciation"] = 0.0
    g = f.groupby("ticker")
    ttm = g[FLOWS].transform(lambda s: s.rolling(4, min_periods=4).sum()).add_suffix("_ttm")
    f = pd.concat([f, ttm], axis=1)
    for c, out in [("sales", "SALES_GROWTH"), ("op_income", "OP_GROWTH")]:
        prev = g[c].shift(4)
        f[out] = (f[c] - prev) / prev.abs().replace(0, np.nan)
    f["ROE"] = f.net_income_ttm / f.equity
    f["ROA"] = f.net_income_ttm / f.assets
    f["OPM"] = f.op_income_ttm / f.sales_ttm
    f["GPOA"] = f.gross_profit_ttm / f.assets
    f["DEBT_RATIO"] = f.liabilities / f.equity
    f["QUICK_RATIO"] = (f.current_assets - f.inventory) / f.current_liabilities
    f["ICR"] = f.op_income_ttm / f.interest_expense_ttm.abs().replace(0, np.nan)
    f["EBITDA_ttm"] = f.op_income_ttm + f.depreciation_ttm
    return f


def build_panel(raw_dir):
    raw = Path(raw_dir)
    px = pd.read_parquet(raw / "prices.parquet")
    px["date"] = pd.to_datetime(px["date"])
    close = px.pivot_table(index="date", columns="ticker", values="close", aggfunc="last").sort_index()

    # ---- price-based block, on a month-end grid (labels = calendar month ends)
    m_close = close.resample("ME").last()
    vol20 = close.pct_change(fill_method=None).rolling(20, min_periods=15).std().resample("ME").last()
    long = pd.DataFrame({
        "RET_1M": m_close.pct_change(1, fill_method=None).stack(),
        "RET_3M": m_close.pct_change(3, fill_method=None).stack(),
        "RET_12M": m_close.pct_change(12, fill_method=None).stack(),
        "VOL_20D": vol20.stack(),
        "ret_next": (m_close.shift(-1) / m_close - 1).stack(),
    })
    long.index.names = ["date", "ticker"]
    last = (px.assign(date=px["date"] + pd.offsets.MonthEnd(0))
              .sort_values("date").groupby(["date", "ticker"])
              .agg(mcap=("mcap", "last"), market=("market", "last"), eligible=("eligible", "last")))
    panel = long.join(last, how="left").reset_index()
    panel = panel[panel["eligible"].fillna(False).astype(bool)]

    # ---- benchmark return for t+1
    if (raw / "index.parquet").exists():
        ix = pd.read_parquet(raw / "index.parquet"); ix["date"] = pd.to_datetime(ix["date"])
        ic = ix.pivot_table(index="date", columns="market", values="close", aggfunc="last").resample("ME").last()
        ir = (ic.shift(-1) / ic - 1).stack().rename("mret").reset_index()
        ir.columns = ["date", "market", "mret"]
        cap = last.reset_index().groupby(["date", "market"])["mcap"].sum().rename("cap").reset_index()
        b = ir.merge(cap, on=["date", "market"]).dropna()
        bench = b.groupby("date").apply(lambda x: np.average(x.mret, weights=x.cap), include_groups=False)
        panel["mkt_next"] = panel["date"].map(bench)
    else:
        w = panel.dropna(subset=["ret_next", "mcap"])
        bench = w.groupby("date").apply(lambda x: np.average(x.ret_next, weights=x.mcap), include_groups=False)
        panel["mkt_next"] = panel["date"].map(bench)

    # ---- fundamentals as of filing date
    f = pd.read_parquet(raw / "fundamentals.parquet")
    f["period_end"] = pd.to_datetime(f["period_end"]); f["filing_date"] = pd.to_datetime(f["filing_date"])
    f = _fundamental_factors(f).sort_values("filing_date")
    keep = ["ticker", "filing_date", "period_end", "SALES_GROWTH", "OP_GROWTH", "ROE", "ROA", "OPM",
            "GPOA", "DEBT_RATIO", "QUICK_RATIO", "ICR", "net_income_ttm", "equity", "cfo_ttm",
            "EBITDA_ttm", "debt", "cash"]
    panel = pd.merge_asof(panel.sort_values("date"), f[keep], left_on="date", right_on="filing_date",
                          by="ticker", direction="backward")
    stale = panel["period_end"] < panel["date"] - pd.DateOffset(months=MAX_STALENESS_MONTHS)
    panel.loc[stale, keep[3:]] = np.nan
    panel["PER"] = panel.mcap / panel.net_income_ttm.replace(0, np.nan)
    panel["PBR"] = panel.mcap / panel.equity.replace(0, np.nan)
    panel["PCR"] = panel.mcap / panel.cfo_ttm.replace(0, np.nan)
    panel["EV_EBITDA"] = (panel.mcap + panel.debt - panel.cash) / panel.EBITDA_ttm.replace(0, np.nan)

    # ---- macro: only figures public by the end of the previous month
    mac = pd.read_parquet(raw / "macro.parquet"); mac["avail_date"] = pd.to_datetime(mac["avail_date"])
    grid = pd.DataFrame({"date": sorted(panel["date"].unique())})
    grid["asof"] = grid["date"] - pd.offsets.MonthEnd(1) + pd.Timedelta(hours=23, minutes=59)
    for name in MACRO:
        s = mac[mac["name"] == name].sort_values("avail_date")[["avail_date", "value"]]
        grid = pd.merge_asof(grid.sort_values("asof"), s, left_on="asof", right_on="avail_date",
                             direction="backward").rename(columns={"value": name}).drop(columns="avail_date")
    panel = panel.merge(grid.drop(columns="asof"), on="date", how="left")

    panel = panel.dropna(subset=["ret_next", "mkt_next"] + MACRO)
    return panel[["date", "ticker"] + ALL_FEATURES + ["ret_next", "mkt_next"]].reset_index(drop=True)

"""Forward-looking factor tests: point-in-time consensus use, R&D annual merge, new momentum factors.
Run: python tests/test_forward.py"""
import sys, tempfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data_real import build_panel
from config import MACRO

MO = pd.date_range("2012-01-31", "2025-12-31", freq="ME")


def make(raw):
    days = pd.bdate_range("2012-06-01", "2026-01-31")
    px = np.exp(np.cumsum(np.random.default_rng(0).normal(0, 0.01, len(days)))) * 100
    pd.DataFrame(dict(date=days, ticker="A", close=px, mcap=1e9, market="KOSPI", eligible=True)).to_parquet(raw / "prices.parquet")
    q = pd.date_range("2011-03-31", "2025-12-31", freq="QE")
    f = pd.DataFrame(dict(ticker="A", period_end=q, filing_date=q + pd.Timedelta(days=45)))
    for c in ["sales", "gross_profit", "op_income", "net_income", "cfo", "interest_expense", "capex"]:
        f[c] = 10.0
    for c in ["equity", "assets", "liabilities", "current_assets", "current_liabilities", "inventory", "cash", "debt"]:
        f[c] = 100.0
    # R&D only on annual rows; filed 90 days after year end. rd = 5 * (year-2010): grows every year
    ann = f.period_end.dt.month == 12
    f["sales_annual"] = np.where(ann, 400.0, np.nan)
    f["rd_annual"] = np.where(ann, 5.0 * (f.period_end.dt.year - 2010), np.nan)
    f.loc[ann, "filing_date"] = f.loc[ann, "period_end"] + pd.Timedelta(days=90)
    f.to_parquet(raw / "fundamentals.parquet")
    pd.concat([pd.DataFrame(dict(name=n, avail_date=MO + pd.Timedelta(days=5), value=1.0)) for n in MACRO]
              ).to_parquet(raw / "macro.parquet")
    rows = []
    for k, s in enumerate(MO):                         # one snapshot per month-end; value encodes the snapshot index
        for off in (0, 1):
            rows.append(dict(ticker="A", snapshot_date=s, target_year=s.year + off, metric="ni", value=100.0 * k + off))
    pd.DataFrame(rows).to_parquet(raw / "consensus.parquet")


with tempfile.TemporaryDirectory() as d:
    raw = Path(d); make(raw)
    k = lambda ts: list(MO).index(pd.Timestamp(ts))
    p = build_panel(raw).set_index("date")
    t = "2020-03-31"
    # 12M-forward NI at March = 9/12*FY2020 + 3/12*FY2021 of the March snapshot = 100*k + 0.25
    assert np.isclose(1e9 / p.loc[t, "FWD_PER"], 100 * k(t) + 0.25), p.loc[t, "FWD_PER"]
    # 3M revision of the SAME fiscal year (2020): now 100*k vs Dec-2019 snapshot's FY2020 = 100*k(Dec19)+1
    prev = 100 * k("2019-12-31") + 1
    assert np.isclose(p.loc[t, "EST_REVISION_3M"], (100 * k(t) - prev) / prev), p.loc[t, "EST_REVISION_3M"]
    # December: fully FY(t+1)
    assert np.isclose(1e9 / p.loc["2020-12-31", "FWD_PER"], 100 * k("2020-12-31") + 1.0)
    # a 40-day publication lag must push the snapshot back two months (Feb-29 snapshot + 40d lands after t)
    pl = build_panel(raw, consensus_lag_days=40).set_index("date")
    assert np.isclose(1e9 / pl.loc[t, "FWD_PER"], 100 * k("2020-01-31") + 0.25)
    # R&D: at 2021-03-31 the FY2020 annual report (filed 2021-03-31) is just usable; at 2021-02-28 only FY2019 is
    assert np.isclose(p.loc["2021-03-31", "RD_INTENSITY"], 5 * 10 / 400)
    assert np.isclose(p.loc["2021-02-28", "RD_INTENSITY"], 5 * 9 / 400)
    assert np.isclose(p.loc["2021-03-31", "RD_GROWTH"], 5 / 45)
    # extended momentum columns exist and are lag-correct: MOM_12_1 uses t-1 .. t-12 only
    assert {"RET_6M", "MOM_12_1", "DIST_52W_HIGH", "CAPEX_INTENSITY", "ASSET_GROWTH", "FWD_SALES_GROWTH"} - set(p.columns) == {"FWD_SALES_GROWTH"}
print("forward-factor tests passed")

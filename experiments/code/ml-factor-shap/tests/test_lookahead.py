"""Look-ahead guards for the real-data builder (run: python tests/test_lookahead.py)."""
import sys, tempfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data_real import build_panel
from config import MACRO


def make(raw):
    days = pd.bdate_range("2012-06-01", "2026-01-31")
    px = pd.DataFrame(dict(date=days, ticker="A", close=np.linspace(100, 200, len(days)),
                           mcap=1e9, market="KOSPI", eligible=True))
    px.to_parquet(raw / "prices.parquet")
    q = pd.date_range("2011-03-31", "2025-12-31", freq="QE")
    f = pd.DataFrame(dict(ticker="A", period_end=q, filing_date=q + pd.Timedelta(days=45)))
    for c in ["sales", "gross_profit", "op_income", "net_income", "cfo", "interest_expense"]:
        f[c] = np.arange(len(q)) + 1.0          # strictly increasing => value identifies the quarter
    for c in ["equity", "assets", "liabilities", "current_assets", "current_liabilities",
              "inventory", "cash", "debt"]:
        f[c] = 1.0
    f.to_parquet(raw / "fundamentals.parquet")
    mo = pd.date_range("2012-01-31", "2025-12-31", freq="ME")
    pd.concat([pd.DataFrame(dict(name=n, avail_date=mo + pd.Timedelta(days=5),
                                 value=np.arange(len(mo), dtype=float))) for n in MACRO]
              ).to_parquet(raw / "macro.parquet")


with tempfile.TemporaryDirectory() as d:
    raw = Path(d); make(raw)
    p = build_panel(raw).set_index("date")
    # macro at 2020-03-31 may use ref-month 2020-01 (public 2020-02-05) but NOT ref-month 2020-02 (public 2020-03-05)
    mo = pd.date_range("2012-01-31", "2025-12-31", freq="ME")
    assert p.loc["2020-03-31", "BASE_RATE"] == list(mo).index(pd.Timestamp("2020-01-31"))
    # 2020-03-31: Q4-2019 (filed 2020-02-14) usable, Q1-2020 (period_end 03-31, filed 05-15) not.
    # With net_income = quarter index, TTM(Q4-2019)=sum of last 4 quarters; PER = mcap/TTM
    q = pd.date_range("2011-03-31", "2025-12-31", freq="QE"); i = list(q).index(pd.Timestamp("2019-12-31"))
    ttm = sum(np.arange(len(q))[i - 3:i + 1] + 1.0)
    assert np.isclose(p.loc["2020-03-31", "PER"], 1e9 / ttm), p.loc["2020-03-31", "PER"]
    # at 2020-05-31 the Q1-2020 filing (2020-05-15) has been public, so the TTM window rolls forward
    assert np.isclose(p.loc["2020-05-31", "PER"], 1e9 / (ttm + (i + 2) - (i - 3 + 1)))
print("look-ahead tests passed")

"""Universe tests: financial/SPAC screen, point-in-time eligibility, exclusions, coverage filter.
Run: python tests/test_universe.py"""
import sys, tempfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MACRO
from data_real import build_panel
from universe import build_eligibility, classify

# --- classification
assert classify("1", "KB금융지주") == (True, False)                      # name fallback
assert classify("2", "삼성전자", sector="전기전자") == (False, False)
assert classify("3", "미래에셋비전스팩1호") == (False, True)
assert classify("4", "삼성전자", sector="금융업") == (True, False)        # sector wins over name
m = pd.DataFrame(dict(month=pd.to_datetime(["2020-01-31"] * 3), ticker=["1", "2", "3"], market="KOSPI"))
e = build_eligibility(m, {"1": "KB금융지주", "2": "삼성전자", "3": "XX스팩"})
assert e.set_index("ticker")["eligible"].to_dict() == {"1": False, "2": True, "3": False}

# --- integrated: A normal, B has no fundamentals, C is excluded for 2020-06..2020-12, D listed only from 2018
def make(raw):
    days = pd.bdate_range("2012-06-01", "2026-01-31")
    rng = np.random.default_rng(0)
    rows = []
    for t in "ABCD":
        px = np.exp(np.cumsum(rng.normal(0, 0.01, len(days)))) * 100
        df = pd.DataFrame(dict(date=days, ticker=t, close=px, mcap=1e9, market="KOSPI", eligible=True))
        if t == "D":
            df["eligible"] = df["date"] >= "2018-01-01"
        rows.append(df)
    pd.concat(rows).to_parquet(raw / "prices.parquet")
    q = pd.date_range("2011-03-31", "2025-12-31", freq="QE")
    fr = []
    for t in "ACD":                                    # B has no statements at all
        f = pd.DataFrame(dict(ticker=t, period_end=q, filing_date=q + pd.Timedelta(days=45)))
        for c in ["sales", "gross_profit", "op_income", "net_income", "cfo", "interest_expense"]:
            f[c] = rng.uniform(5, 10, len(q))
        for c in ["equity", "assets", "liabilities", "current_assets", "current_liabilities", "inventory", "cash", "debt"]:
            f[c] = rng.uniform(50, 100, len(q))
        fr.append(f)
    pd.concat(fr).to_parquet(raw / "fundamentals.parquet")
    mo = pd.date_range("2012-01-31", "2025-12-31", freq="ME")
    pd.concat([pd.DataFrame(dict(name=n, avail_date=mo + pd.Timedelta(days=5), value=1.0)) for n in MACRO]
              ).to_parquet(raw / "macro.parquet")
    pd.DataFrame(dict(ticker=["C"], start=["2020-06-01"], end=["2020-12-31"])).to_csv(raw / "exclusions.csv", index=False)


with tempfile.TemporaryDirectory() as d:
    raw = Path(d); make(raw)
    p = build_panel(raw)
    have = lambda t: set(p.loc[p.ticker == t, "date"])
    assert not have("B"), "ticker without statements must be dropped by the coverage filter"
    assert not any(pd.Timestamp("2020-06-30") <= x <= pd.Timestamp("2020-12-31") for x in have("C"))
    assert pd.Timestamp("2020-03-31") in have("C") and pd.Timestamp("2021-03-31") in have("C")
    assert min(have("D")) >= pd.Timestamp("2018-01-31"), "ineligible months (not yet listed) must be excluded"
    kept = build_panel(raw, min_coverage=0.0)
    assert "B" in set(kept.ticker), "coverage filter off keeps B"
print("universe tests passed")

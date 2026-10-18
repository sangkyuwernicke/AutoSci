"""DART conversion / cache / call-limit tests with a fake OpenDartReader client. Run: python tests/test_fetch.py"""
import sys, tempfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fetch_real_data as fr

# (sales 3M, add) per report; capex is cash-flow YTD; equity is point-in-time
SALES = {"11013": (10, None), "11012": (12, 22), "11014": (15, 37), "11011": (60, None)}
CAPEX_YTD = {"11013": 5, "11012": 11, "11014": 18, "11011": 30}
FILED = {"11013": "20200515", "11012": "20200814", "11014": "20201113", "11011": "20210331"}


class FakeDart:
    def __init__(self):
        self.calls = 0

    def finstate_all(self, t, year, reprt_code="11011", fs_div="CFS"):
        self.calls += 1
        if year != 2020:
            return None
        amt, add = SALES[reprt_code]
        rows = [
            dict(account_id="ifrs-full_Revenue", account_nm="매출액", thstrm_amount=f"{amt:,}", thstrm_add_amount=add),
            dict(account_id="ifrs-full_PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities",
                 account_nm="유형자산의 취득", thstrm_amount=str(CAPEX_YTD[reprt_code]), thstrm_add_amount=None),
            dict(account_id="ifrs-full_Equity", account_nm="자본총계", thstrm_amount="1,000", thstrm_add_amount=None),
        ]
        if reprt_code == "11011":
            rows.append(dict(account_id="dart_X", account_nm="경상연구개발비", thstrm_amount="6", thstrm_add_amount=None))
        d = pd.DataFrame(rows)
        d["rcept_no"] = FILED[reprt_code] + "000123"
        return d


fr.START, fr.END = "2020-01-01", "2020-12-31"
dart = FakeDart()
q = fr._fetch_one(dart, "000010", [2019, 2020]).set_index("period_end")
assert dart.calls == 8
assert q.loc["2020-03-31", "sales"] == 10 and q.loc["2020-06-30", "sales"] == 12
assert q.loc["2020-09-30", "sales"] == 15 and q.loc["2020-12-31", "sales"] == 23     # 60 - 37
assert list(q["capex"]) == [5, 6, 7, 12]                                              # YTD cash flow -> quarters
assert (q["equity"] == 1000).all()                                                    # balance sheet is not differenced
assert q.loc["2020-12-31", "rd_annual"] == 6 and q.loc["2020-12-31", "sales_annual"] == 60
assert q.loc["2020-06-30", "filing_date"] == pd.Timestamp("2020-08-14")               # filing date from rcept_no

with tempfile.TemporaryDirectory() as d:
    out = Path(d)
    pd.DataFrame(dict(date=pd.to_datetime(["2020-01-31"] * 3), ticker=["000010", "000020", "000030"],
                      market=["KOSPI", "KOSPI", "KOSDAQ"], mcap=[3.0, 2.0, 9.0], eligible=True)
                 ).to_parquet(out / "prices_monthly.parquet")
    assert fr.select_tickers(out, "KOSPI", 0) == ["000010", "000020"]
    assert fr.select_tickers(out, None, 1) == ["000030"]
    fr._dart_client = lambda: dart
    dart.calls = 0
    fr.fetch_fundamentals(out, ["000010", "000020"], start_year=2020, max_calls=100)
    assert dart.calls == 2 * 1 * 4
    f = pd.read_parquet(out / "fundamentals.parquet")
    assert set(f.ticker) == {"000010", "000020"} and len(f) == 8
    dart.calls = 0
    fr.fetch_fundamentals(out, ["000010", "000020"], start_year=2020, max_calls=100)
    assert dart.calls == 0, "cached tickers must not be fetched again"
    try:
        fr.fetch_fundamentals(out, ["000099"], start_year=2012, max_calls=10)
        raise AssertionError("call limit not enforced")
    except SystemExit:
        pass
print("fetch tests passed")

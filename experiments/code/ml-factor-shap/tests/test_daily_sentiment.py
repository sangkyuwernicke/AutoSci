"""Daily sentiment tests: weekend roll-forward, entry timing (no look-ahead), daily rank IC, long-short accounting.
Run: python tests/test_daily_sentiment.py"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from daily_sentiment_ic import attach_returns, daily_ic, forward_returns, quantile_backtest, to_trading_days

CAL = pd.bdate_range("2025-01-06", "2025-01-17")                  # 10 trading days, Mon..Fri x2
CLOSE = pd.DataFrame({"A": [100, 101, 103, 106, 110, 115, 121, 128, 136, 145], "B": 100.0}, index=CAL, dtype=float)


def test_weekend_news_rolls_to_next_trading_day():
    d = pd.DataFrame({"ticker": "A",
                      "date": pd.to_datetime(["2025-01-10", "2025-01-11", "2025-01-13", "2025-01-18"]),
                      "n_articles": [1, 3, 1, 2], "mean_score": [0.5, -0.5, 1.0, 0.9]})
    s = to_trading_days(d, CAL).set_index("date")
    assert np.isclose(s.loc["2025-01-10", "mean_score"], 0.5) and s.loc["2025-01-10", "n_articles"] == 1
    assert np.isclose(s.loc["2025-01-13", "mean_score"], (3 * -0.5 + 1.0) / 4) and s.loc["2025-01-13", "n_articles"] == 4
    assert len(s) == 2, "news after the last trading day has no entry price and must be dropped"


def test_entry_timing_and_horizon():
    dates = pd.DatetimeIndex([CAL[2], CAL[3]])
    a0 = forward_returns(CLOSE, dates, horizon=1, entry_shift=0)["A"]
    b0 = forward_returns(CLOSE, dates, horizon=1, entry_shift=1)["A"]
    assert np.isclose(a0[CAL[2]], 106 / 103 - 1)                  # A: enter at the signal day's close
    assert np.isclose(b0[CAL[2]], 110 / 106 - 1)                  # B: enter one trading day later
    assert np.isclose(forward_returns(CLOSE, dates, horizon=2, entry_shift=0)["A"][CAL[2]], 110 / 103 - 1)
    assert forward_returns(CLOSE, pd.DatetimeIndex([CAL[-1]]), 1, 0).isna().all().all(), "no price after the last day"
    # B never touches the signal day's close: perturbing it must not change a B return
    bumped = CLOSE.copy()
    bumped.loc[CAL[2], "A"] = 999.0
    assert np.isclose(forward_returns(bumped, dates, 1, 1)["A"][CAL[2]], b0[CAL[2]])
    assert not np.isclose(forward_returns(bumped, dates, 1, 0)["A"][CAL[2]], a0[CAL[2]])


def test_daily_ic():
    rows = [dict(date=CAL[0], ticker=f"t{i}", mean_score=float(i), ret=0.01 * i) for i in range(10)]      # perfect rank
    rows += [dict(date=CAL[1], ticker=f"t{i}", mean_score=float(i), ret=-0.01 * i) for i in range(10)]    # perfectly inverse
    rows += [dict(date=CAL[2], ticker=f"t{i}", mean_score=float(i), ret=0.01 * i) for i in range(5)]      # too few stocks
    ic = daily_ic(pd.DataFrame(rows), min_n=8)
    assert np.isclose(ic[CAL[0]], 1.0) and np.isclose(ic[CAL[1]], -1.0) and CAL[2] not in ic.index


def test_quantile_backtest_accounting():
    rows = []
    for d in (CAL[0], CAL[1], CAL[4]):                             # day 0 and 1 adjacent, day 4 after a gap
        rows += [dict(date=d, ticker=f"t{i}", mean_score=float(i), ret=0.01 * i, n_articles=1) for i in range(1, 11)]
    bt = quantile_backtest(pd.DataFrame(rows), CAL, q=0.2, min_n=10, cost=0.002).set_index("date")
    # k = 2: long t9,t10 (mean ret 0.095), short t1,t2 (0.015); long-only excess vs the 10-stock mean (0.055)
    assert np.isclose(bt.loc[CAL[0], "ls_gross"], 0.080) and np.isclose(bt.loc[CAL[0], "lo_excess_gross"], 0.040)
    assert np.isclose(bt.loc[CAL[0], "ls_turnover"], 2.0) and np.isclose(bt.loc[CAL[0], "ls_net"], 0.080 - 0.002 * 2.0)
    assert np.isclose(bt.loc[CAL[0], "lo_turnover"], 1.0)
    assert np.isclose(bt.loc[CAL[1], "ls_turnover"], 0.0) and np.isclose(bt.loc[CAL[1], "ls_net"], 0.080)   # same book
    assert np.isclose(bt.loc[CAL[4], "ls_turnover"], 2.0), "after a gap the book is rebuilt from scratch"


for t in (test_weekend_news_rolls_to_next_trading_day, test_entry_timing_and_horizon, test_daily_ic,
          test_quantile_backtest_accounting):
    t()
print("daily-sentiment tests passed")

"""Weekly sentiment tests: trailing 5-day signal, no look-ahead, rebalance phases, step-aware turnover.
Run: python tests/test_weekly_sentiment.py"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from daily_sentiment_ic import quantile_backtest
from weekly_sentiment_ic import rebalance_dates, trailing_signal

CAL = pd.bdate_range("2025-01-06", "2025-01-31")                  # 20 trading days


def rows(*items):
    return pd.DataFrame([dict(ticker="A", date=CAL[i], n_articles=n, mean_score=m) for i, n, m in items])


def test_trailing_window_values():
    sig = rows((2, 2, 1.0), (4, 1, -1.0), (7, 1, 0.5))
    out = trailing_signal(sig, CAL, window=5).set_index("date")
    assert CAL[1] not in out.index, "no news in the window -> no signal"
    assert np.isclose(out.loc[CAL[4], "mean_score"], (2 * 1.0 - 1.0) / 3) and out.loc[CAL[4], "n_articles"] == 3
    assert np.isclose(out.loc[CAL[6], "mean_score"], 1 / 3)       # idx 2..6 still holds idx 2 and idx 4
    assert np.isclose(out.loc[CAL[7], "mean_score"], (-1.0 + 0.5) / 2) and out.loc[CAL[7], "n_articles"] == 2
    assert CAL[12] not in out.index, "idx 8..12 holds nothing"


def test_trailing_window_has_no_lookahead():
    base = trailing_signal(rows((2, 2, 1.0), (4, 1, -1.0)), CAL, 5).set_index("date")
    plus_future = trailing_signal(rows((2, 2, 1.0), (4, 1, -1.0), (6, 9, 1.0), (15, 9, -1.0)), CAL, 5).set_index("date")
    for d in CAL[:6]:                                             # rows dated after d must not move the signal at d
        if d in base.index:
            assert np.isclose(base.loc[d, "mean_score"], plus_future.loc[d, "mean_score"])
            assert base.loc[d, "n_articles"] == plus_future.loc[d, "n_articles"]


def test_rebalance_phases_partition_the_calendar():
    ph = [rebalance_dates(CAL, step=5, phase=p) for p in range(5)]
    assert all(len(x) == 4 for x in ph) and ph[2][0] == CAL[2] and ph[2][1] == CAL[7]
    assert sorted(np.concatenate([x.values for x in ph])) == sorted(CAL.values)


def test_step_aware_turnover():
    def book(day):
        return [dict(date=CAL[day], ticker=f"t{i}", mean_score=float(i), ret=0.01 * i, n_articles=1) for i in range(1, 11)]
    sig = pd.DataFrame(book(0) + book(5) + book(11))             # 0 -> 5 is one weekly step, 5 -> 11 is a gap
    bt = quantile_backtest(sig, CAL, q=0.2, min_n=10, cost=0.002, step=5).set_index("date")
    assert np.isclose(bt.loc[CAL[0], "ls_turnover"], 2.0)
    assert np.isclose(bt.loc[CAL[5], "ls_turnover"], 0.0), "same book one step later: nothing traded"
    assert np.isclose(bt.loc[CAL[11], "ls_turnover"], 2.0), "gap -> rebuilt"
    daily = quantile_backtest(sig, CAL, q=0.2, min_n=10, cost=0.002).set_index("date")
    assert np.isclose(daily.loc[CAL[5], "ls_turnover"], 2.0), "default step=1 keeps the old daily meaning"


for t in (test_trailing_window_values, test_trailing_window_has_no_lookahead,
          test_rebalance_phases_partition_the_calendar, test_step_aware_turnover):
    t()
print("weekly-sentiment tests passed")

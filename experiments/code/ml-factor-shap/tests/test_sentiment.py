"""News-sentiment factor tests: hand-computed windows, no look-ahead, empty months, build_panel wiring.
Run: python tests/test_sentiment.py"""
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MACRO, SENTIMENT_FACTORS
from data_real import build_panel
from sentiment import monthly_sentiment_features

T = pd.Timestamp("2020-03-31")


def daily_rows():
    # (date, n_articles, mean_score) for ticker A. Window end e = T - lag(1d) = 2020-03-30.
    rows = [("2020-03-30", 2, 0.5), ("2020-03-25", 1, -0.5), ("2020-03-05", 1, 1.0),
            ("2020-02-10", 2, 0.0),                      # outside 1M window, inside 3M window
            ("2020-03-31", 5, -1.0),                     # dated on T itself: excluded when lag=1
            ("2020-04-02", 3, 1.0)]                      # after T: never allowed
    return pd.DataFrame(rows, columns=["date", "n_articles", "mean_score"]).assign(
        ticker="A", date=lambda d: pd.to_datetime(d["date"]))


def feats(daily, lag=1):
    f = monthly_sentiment_features(daily, pd.DatetimeIndex([T]), ["A", "B"], lag_days=lag)
    return f.set_index("ticker")


def test_hand_computed_windows():
    a = feats(daily_rows()).loc["A"]
    assert np.isclose(a["SENT_MEAN_1W"], (2 * 0.5 + 1 * -0.5) / 3)
    assert np.isclose(a["SENT_MEAN_1M"], (1.0 - 0.5 + 1.0) / 4)
    assert np.isclose(a["SENT_MEAN_3M"], (1.0 - 0.5 + 1.0 + 0.0) / 6)
    assert np.isclose(a["SENT_CHG"], (2 * 0.5 + 1 * -0.5) / 3 - 1.0)      # last week minus the prior 23 days
    assert np.isclose(a["SENT_STD_1M"], np.std([0.5, -0.5, 1.0], ddof=1))  # std of per-day means (3 news-days)
    assert np.isclose(a["NEWS_COUNT_1M"], np.log1p(4))


def test_no_lookahead():
    base = feats(daily_rows()).loc["A"]
    d = daily_rows()
    cut = d[d["date"] <= T - pd.Timedelta(days=1)]                          # drop everything the lag forbids
    pd.testing.assert_series_equal(base, feats(cut).loc["A"])
    shifted = d.assign(mean_score=np.where(d["date"] >= T, -0.123, d["mean_score"]))
    pd.testing.assert_series_equal(base, feats(shifted).loc["A"])           # perturbing T / future news changes nothing
    assert feats(d, lag=0).loc["A", "SENT_MEAN_1W"] != base["SENT_MEAN_1W"]  # lag really is what excludes day T


def test_empty_and_sparse():
    b = feats(daily_rows()).loc["B"]
    assert b["NEWS_COUNT_1M"] == 0 and b[[c for c in SENTIMENT_FACTORS if c != "NEWS_COUNT_1M"]].isna().all()
    two_days = daily_rows().iloc[:2]                                         # only 2 news-days -> std undefined
    assert np.isnan(feats(two_days).loc["A", "SENT_STD_1M"])
    assert set(SENTIMENT_FACTORS) <= set(feats(daily_rows()).columns)


def test_output_keys_unique_and_complete():
    f = monthly_sentiment_features(daily_rows(), pd.DatetimeIndex([T, T + pd.offsets.MonthEnd(1)]), ["A", "B"])
    assert len(f) == 4 and not f.duplicated(["ticker", "date"]).any()


def make_raw(raw):
    days = pd.bdate_range("2019-06-01", "2021-03-31")
    px = np.exp(np.cumsum(np.random.default_rng(0).normal(0, 0.01, len(days)))) * 100
    pd.DataFrame(dict(date=days, ticker="A", close=px, mcap=1e9, market="KOSPI", eligible=True)).to_parquet(raw / "prices.parquet")
    q = pd.date_range("2018-03-31", "2021-03-31", freq="QE")
    f = pd.DataFrame(dict(ticker="A", period_end=q, filing_date=q + pd.Timedelta(days=45)))
    for c in ["sales", "gross_profit", "op_income", "net_income", "cfo", "interest_expense", "capex"]:
        f[c] = 10.0
    for c in ["equity", "assets", "liabilities", "current_assets", "current_liabilities", "inventory", "cash", "debt"]:
        f[c] = 100.0
    f.to_parquet(raw / "fundamentals.parquet")
    mo = pd.date_range("2018-12-31", "2021-03-31", freq="ME")
    pd.concat([pd.DataFrame(dict(name=n, avail_date=mo + pd.Timedelta(days=5), value=1.0)) for n in MACRO]
              ).to_parquet(raw / "macro.parquet")
    daily_rows().to_parquet(raw / "sentiment_finbert.parquet")


def test_build_panel_wiring():
    with tempfile.TemporaryDirectory() as d:
        raw = Path(d)
        make_raw(raw)
        off = build_panel(raw).set_index("date")
        on = build_panel(raw, sentiment="finbert").set_index("date")
        assert not set(SENTIMENT_FACTORS) & set(off.columns), "sentiment must be opt-in"
        assert set(SENTIMENT_FACTORS) <= set(on.columns)
        assert np.isclose(on.loc[T, "SENT_MEAN_1M"], 0.375)
        assert on.loc["2020-05-31", "NEWS_COUNT_1M"] == 0 and np.isnan(on.loc["2020-05-31", "SENT_MEAN_1M"])
        assert len(on) == len(off)                                           # sentiment never drops rows
        try:
            build_panel(raw, sentiment="nope")
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("missing sentiment file must fail loudly")


def test_avg_stocks_per_month():
    from factor_ic import avg_stocks_per_month
    p = pd.DataFrame({"date": pd.to_datetime(["2020-01-31"] * 4 + ["2020-02-29"] * 2),
                      "ticker": list("abcdab"),
                      "X": [1.0, np.nan, 3.0, 4.0, 5.0, np.nan],        # 3 valid in Jan, 1 valid in Feb
                      "Y": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]})
    n = avg_stocks_per_month(p, ["X", "Y"])
    assert np.isclose(n["X"], 2.0) and np.isclose(n["Y"], 3.0), n.to_dict()    # mean over months of valid count


def test_residualize_removes_control_signal():
    from factor_ic import add_residuals, monthly_rank_ic
    rng = np.random.default_rng(0)
    months = []
    for d in pd.date_range("2020-01-31", periods=24, freq="ME"):
        r = rng.normal(size=60)
        x = 2 * r + rng.normal(scale=0.3, size=60)          # X is almost a function of the control RET_1M
        x[:10] = np.nan                                       # sparse factor: 10 stocks without a value
        months.append(pd.DataFrame({"date": d, "ticker": range(60), "RET_1M": r, "X": x,
                                    "ret_next": 0.01 * r, "mkt_next": 0.0}))   # next return driven only by RET_1M
    p = pd.concat(months, ignore_index=True)
    q = add_residuals(p, ["X"], ["RET_1M"])
    assert q["X_RES"].isna().sum() == p["X"].isna().sum(), "missing pattern must be preserved"
    ic = monthly_rank_ic(q, ["X", "X_RES"], min_n=20).mean()
    assert ic["X"] > 0.8 and abs(ic["X_RES"]) < 0.15, ic.to_dict()   # the whole raw IC came from the control
    g = q[(q["date"] == q["date"].iloc[0]) & q["X_RES"].notna()]
    assert abs(np.corrcoef(g["X_RES"], g["RET_1M"].rank())[0, 1]) < 1e-8     # orthogonal to the control's rank
    assert "X_RES" not in p.columns, "input panel must not be mutated"


for t in (test_hand_computed_windows, test_no_lookahead, test_empty_and_sparse,
          test_output_keys_unique_and_complete, test_build_panel_wiring, test_avg_stocks_per_month,
          test_residualize_removes_control_signal):
    t()
print("sentiment-factor tests passed")

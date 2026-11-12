"""Monthly news-sentiment factors from a daily ticker x date sentiment table.

The daily table (see prepare_sentiment.py) has one row per (ticker, date) that had news:
    ticker, date, n_articles, mean_score   (mean_score in [-1, 1], mean over that day's articles)

For a month-end t the window ends at e = t - lag_days (inclusive), so nothing dated after e is used. The default
lag of 1 day keeps news published on t itself out: it may appear after the close the label is measured from.
All windows are calendar-day windows ending at e; sums come from prefix sums, so any window is O(1).

  SENT_MEAN_1W   article-weighted mean score over (e-7, e]
  SENT_MEAN_1M   ... over (e-30, e]
  SENT_MEAN_3M   ... over (e-90, e]
  SENT_CHG       SENT_MEAN_1W minus the mean over the prior 23 days (e-30, e-7]  (short-term momentum of tone)
  SENT_STD_1M    std of the per-day mean scores over (e-30, e]; needs >= MIN_NEWS_DAYS news-days
  NEWS_COUNT_1M  log(1 + articles in (e-30, e])  -- attention; 0 when there was no news

No news in a window is NaN (not neutral 0): the cross-sectional transform later maps NaN to the monthly median,
and NEWS_COUNT_1M tells the model that the value was missing.
"""
import numpy as np
import pandas as pd

MIN_NEWS_DAYS = 3
WINDOW_DAYS = {"1W": 7, "1M": 30, "3M": 90}


def _prefix_sums(daily: pd.DataFrame, cal: pd.DatetimeIndex, tickers: list) -> dict:
    """Prefix sums over the calendar, row 0 = empty prefix; C[i] = sum of days cal[:i]."""
    n, m = daily["n_articles"].to_numpy(float), daily["mean_score"].to_numpy(float)
    parts = {"N": n, "S": n * m, "D": np.ones(len(daily)), "M": m, "M2": m * m}
    ti = pd.Index(tickers).get_indexer(daily["ticker"])
    di = cal.get_indexer(daily["date"])
    out = {}
    for k, v in parts.items():
        mat = np.zeros((len(cal), len(tickers)))
        np.add.at(mat, (di, ti), v)
        out[k] = np.vstack([np.zeros((1, len(tickers))), np.cumsum(mat, axis=0)])
    return out


def monthly_sentiment_features(daily: pd.DataFrame, month_ends: pd.DatetimeIndex, tickers, lag_days: int = 1):
    """One row per (ticker, month-end) with the SENTIMENT_FACTORS columns."""
    tickers = list(dict.fromkeys(tickers))
    d = daily[["ticker", "date", "n_articles", "mean_score"]].copy()
    d["date"] = pd.to_datetime(d["date"]).dt.normalize()
    d = d[d["ticker"].isin(tickers) & (d["n_articles"] > 0)]
    if d.duplicated(["ticker", "date"]).any():
        raise ValueError("sentiment table must have one row per (ticker, date)")
    month_ends = pd.DatetimeIndex(month_ends)
    ends = month_ends - pd.Timedelta(days=lag_days)
    start = min(d["date"].min() if len(d) else ends.min(), ends.min() - pd.Timedelta(days=WINDOW_DAYS["3M"] + 1))
    cal = pd.date_range(start, max(d["date"].max() if len(d) else ends.max(), ends.max()), freq="D")
    C = _prefix_sums(d, cal, tickers)

    def upto(x):                                             # prefix row holding everything dated <= x
        return cal.searchsorted(x, side="right")

    def win(key, lo_days, hi_days=0):                        # sum over (e - lo_days, e - hi_days]
        return C[key][upto(ends - pd.Timedelta(days=hi_days))] - C[key][upto(ends - pd.Timedelta(days=lo_days))]

    def wmean(lo_days, hi_days=0):
        n, s = win("N", lo_days, hi_days), win("S", lo_days, hi_days)
        return np.where(n > 0.5, s / np.where(n > 0.5, n, 1.0), np.nan)

    m1w, m1m, m3m = (wmean(WINDOW_DAYS[w]) for w in ("1W", "1M", "3M"))
    prior = wmean(WINDOW_DAYS["1M"], WINDOW_DAYS["1W"])
    nd, sm, sm2 = (win(k, WINDOW_DAYS["1M"]) for k in ("D", "M", "M2"))
    ok = nd >= MIN_NEWS_DAYS - 0.5
    var = (sm2 - sm * sm / np.where(ok, nd, 1.0)) / np.where(ok, nd - 1.0, 1.0)
    feats = {"SENT_MEAN_1W": m1w, "SENT_MEAN_1M": m1m, "SENT_MEAN_3M": m3m, "SENT_CHG": m1w - prior,
             "SENT_STD_1M": np.where(ok, np.sqrt(np.maximum(var, 0.0)), np.nan),
             "NEWS_COUNT_1M": np.log1p(win("N", WINDOW_DAYS["1M"]))}
    idx = pd.MultiIndex.from_product([month_ends, tickers], names=["date", "ticker"])
    out = pd.DataFrame({k: v.reshape(-1) for k, v in feats.items()}, index=idx).reset_index()
    return out[["ticker", "date", *feats]]

"""Target construction and cross-sectional preprocessing (winsorize -> rank-gauss / z-score).

Every transform is applied *within a month*, so it uses no information from other dates.
"""
import numpy as np
import pandas as pd
from scipy.stats import norm

from config import FIRM_FACTORS, INVERT_BEFORE_RANK


def add_target(panel, margin=0.0, quantile=None, direction=False):
    """Binary label. Also adds `label_year` (year of month t+1).

    direction=True: y = 1 if the stock's own next-month return is positive (absolute up/down). The label does
                    not depend on the other stocks, so the target stays stable across months; stocks are then
                    ranked by predicted P(up) and the top 20 % are held. Use this as the primary label.

    quantile=None : y = 1 if R_i,t+1 - R_m,t+1 > margin.
    quantile=0.8  : y = 1 for the top (1-quantile) share of stocks by excess return *within each month*
                    (ceil, ties broken by order), so the positive rate is fixed at ~20% every month.
    """
    if sum([quantile is not None, margin != 0.0, direction]) > 1:
        raise ValueError("use only one of direction, margin, quantile")
    p = panel.dropna(subset=["ret_next", "mkt_next"]).copy()
    p["excess"] = p["ret_next"] - p["mkt_next"]
    if direction:
        p["y"] = (p["ret_next"] > 0).astype(int)
    elif quantile is None:
        p["y"] = (p["excess"] > margin).astype(int)
    else:
        if not 0.0 < quantile < 1.0:
            raise ValueError("quantile must be in (0, 1)")
        g = p.groupby("date")["excess"]
        k = np.ceil((1 - quantile) * g.transform("count"))
        p["y"] = (g.rank(ascending=False, method="first") <= k).astype(int)
    p["label_year"] = (p["date"] + pd.offsets.MonthEnd(1)).dt.year
    return p.sort_values(["date", "ticker"]).reset_index(drop=True)


def impute_ffill(panel, cols, max_missing=0.3):
    """Time-series imputation, no look-ahead: forward-fill each ticker's last observed value (the latest earlier
    filing / price window) and never back-fill. Factors still missing in more than `max_missing` of rows are dropped.
    Returns (panel, kept_cols, report) where report lists missing shares before / after the fill."""
    p = panel.sort_values(["ticker", "date"]).copy()
    before = p[cols].replace([np.inf, -np.inf], np.nan).isna().mean()
    p[cols] = p.groupby("ticker")[cols].ffill()
    after = p[cols].replace([np.inf, -np.inf], np.nan).isna().mean()
    kept = [c for c in cols if after[c] <= max_missing]
    rep = pd.DataFrame({"missing_before": before, "missing_after_ffill": after, "kept": after <= max_missing})
    return p.sort_values(["date", "ticker"]).reset_index(drop=True), kept, rep


def cross_sectional_transform(panel, cols=FIRM_FACTORS, winsor=0.01, method="quantile"):
    """Winsorize at [winsor, 1-winsor] per date, then Z-score or quantile->normal.
    Residual NaN (after impute_ffill) -> 0, which is the cross-sectional median of the transformed factor,
    i.e. a median imputation; the share is small and reported by run_experiment."""
    out = panel.reset_index(drop=True).copy()
    X = out[cols].astype(float)
    for c in set(INVERT_BEFORE_RANK) & set(cols):
        X[c] = 1.0 / X[c]
    X = X.replace([np.inf, -np.inf], np.nan)

    d = out["date"]
    lo = X.groupby(d).quantile(winsor).reindex(d).to_numpy()
    hi = X.groupby(d).quantile(1 - winsor).reindex(d).to_numpy()
    X = pd.DataFrame(np.clip(X.to_numpy(), lo, hi), columns=cols)

    g = X.groupby(d)
    if method == "zscore":
        Z = (X - g.transform("mean")) / g.transform("std").replace(0, np.nan)
    elif method == "quantile":
        u = (g.rank() - 0.5) / g.transform("count")
        Z = pd.DataFrame(norm.ppf(u.to_numpy()), columns=cols)
    else:
        raise ValueError(method)
    out[cols] = Z.fillna(0.0).to_numpy()
    return out


def macro_to_regime(panel, cols):
    """Replace each macro level by a coarse regime: 1 if above its *expanding* median up to that month, 0 if
    below, 0.5 if equal. Uses only the past (the median at month t includes t, which is public at t), so no
    look-ahead. Three values per variable instead of ~70 distinct levels leaves a tree little room to memorise
    which month a row belongs to. Raw levels are kept as `<col>_RAW` for describing regimes afterwards."""
    out = panel.copy()
    monthly = out.groupby("date")[cols].first().sort_index()
    reg = pd.DataFrame(0.5, index=monthly.index, columns=cols)
    for c in cols:
        med = monthly[c].expanding(min_periods=1).median()
        reg[c] = np.sign(monthly[c] - med).map({1.0: 1.0, -1.0: 0.0, 0.0: 0.5})
    for c in cols:
        out[f"{c}_RAW"] = out[c]
        out[c] = out["date"].map(reg[c]).to_numpy()
    return out

"""Target construction and cross-sectional preprocessing (winsorize -> rank-gauss / z-score).

Every transform is applied *within a month*, so it uses no information from other dates.
"""
import numpy as np
import pandas as pd
from scipy.stats import norm

from config import FIRM_FACTORS, INVERT_BEFORE_RANK


def add_target(panel, margin=0.0):
    """y = 1 if R_i,t+1 - R_m,t+1 > margin. Also adds `label_year` (year of month t+1)."""
    p = panel.dropna(subset=["ret_next", "mkt_next"]).copy()
    p["excess"] = p["ret_next"] - p["mkt_next"]
    p["y"] = (p["excess"] > margin).astype(int)
    p["label_year"] = (p["date"] + pd.offsets.MonthEnd(1)).dt.year
    return p.sort_values(["date", "ticker"]).reset_index(drop=True)


def cross_sectional_transform(panel, cols=FIRM_FACTORS, winsor=0.01, method="quantile"):
    """Winsorize at [winsor, 1-winsor] per date, then Z-score or quantile->normal. NaN -> 0."""
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

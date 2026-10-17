"""Data-quality report for the assembled panel (printed and saved by run_experiment for real data)."""
import numpy as np
import pandas as pd


def quality_report(panel, cols):
    """Per feature: overall / per-year missing rate, share of zeros, share beyond the 1/99 cross-sectional
    percentiles, and coverage in the first vs. last year (to spot series that start late)."""
    p = panel.copy()
    p["year"] = p["date"].dt.year
    rows = {}
    for c in cols:
        x = p[c].replace([np.inf, -np.inf], np.nan)
        lo = x.groupby(p["date"]).transform(lambda s: s.quantile(0.01))
        hi = x.groupby(p["date"]).transform(lambda s: s.quantile(0.99))
        na_year = x.isna().groupby(p["year"]).mean()
        rows[c] = dict(missing=x.isna().mean(), zero=(x == 0).mean(), outside_1_99=((x < lo) | (x > hi)).mean(),
                       missing_first_year=na_year.iloc[0], missing_last_year=na_year.iloc[-1],
                       worst_year=int(na_year.idxmax()), worst_year_missing=na_year.max())
    out = pd.DataFrame(rows).T
    n = p.groupby("date")["ticker"].nunique()
    print(f"[data quality] {len(p):,} rows, {p.ticker.nunique()} tickers, "
          f"{n.min()}-{n.max()} stocks/month (median {int(n.median())})")
    bad = out[out.missing > 0.3]
    if len(bad):
        print("[data quality] >30% missing:\n" + bad[["missing", "worst_year", "worst_year_missing"]].round(3).to_string())
    return out

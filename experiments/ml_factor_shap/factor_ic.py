"""Single-factor diagnostics before any machine learning: monthly cross-sectional rank IC between each factor
at month-end t and the excess return over month t+1 (stock return minus benchmark return).

    python factor_ic.py --data real --raw-dir data/real --market KOSPI --top-n-mcap 100 --start-date 2020-01-02
    python factor_ic.py --data real --raw-dir data/real --price-only              # whole eligible universe, no DART

Reading it: IC > 0 means a high factor value goes with a higher next-month excess return. Value ratios are
inverted first (E/P, B/P, ...), so a positive IC on PER means cheap stocks did better. `t_nw` is the mean IC over its
Newey-West (lag 3) standard error; |t| < 2 is indistinguishable from noise. If no factor shows an IC and the models
also sit at AUC 0.5, the data (not the model) has nothing to learn from at this sample size.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from config import FACTOR_SETS, INVERT_BEFORE_RANK


def monthly_rank_ic(panel, factors, min_n=20):
    """DataFrame[date x factor] of Spearman correlations with the next-month excess return."""
    p = panel.copy()
    p["excess"] = p["ret_next"] - p["mkt_next"]
    rows = {}
    for d, g in p.groupby("date"):
        r = {}
        for f in factors:
            x = g[f].astype(float)
            if f in INVERT_BEFORE_RANK:
                x = (1.0 / x).replace([np.inf, -np.inf], np.nan)
            ok = x.notna() & g["excess"].notna()
            r[f] = spearmanr(x[ok], g.loc[ok, "excess"])[0] if ok.sum() >= min_n and x[ok].nunique() > 1 else np.nan
        rows[d] = r
    return pd.DataFrame(rows).T.sort_index()


def newey_west_t(x, lag=3):
    x = pd.Series(x).dropna().to_numpy()
    n = len(x)
    if n < lag + 3:
        return np.nan
    e = x - x.mean()
    var = e @ e / n
    for k in range(1, lag + 1):
        var += 2 * (1 - k / (lag + 1)) * (e[k:] @ e[:-k]) / n
    return x.mean() / np.sqrt(var / n) if var > 0 else np.nan


def summarize(ic):
    s = pd.DataFrame({
        "n_months": ic.notna().sum(), "mean_ic": ic.mean(), "sd_ic": ic.std(),
        "t_nw": ic.apply(newey_west_t), "hit_rate": (ic > 0).sum() / ic.notna().sum(),
    })
    s["icir_annual"] = s["mean_ic"] / s["sd_ic"] * np.sqrt(12)
    by_year = ic.groupby(ic.index.year).mean().T
    by_year.columns = [f"ic_{c}" for c in by_year.columns]
    return pd.concat([s, by_year], axis=1).sort_values("t_nw", key=lambda v: v.abs(), ascending=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", choices=["synthetic", "real"], default="real")
    ap.add_argument("--raw-dir", default="data/real")
    ap.add_argument("--out", default="results/factor_ic")
    ap.add_argument("--factor-set", choices=list(FACTOR_SETS), default="extended")
    ap.add_argument("--price-only", action="store_true", help="real: price/size factors on the whole universe")
    ap.add_argument("--market", choices=["ALL", "KOSPI", "KOSDAQ"], default="ALL")
    ap.add_argument("--top-n-mcap", type=int, default=0)
    ap.add_argument("--min-coverage", type=float, default=0.5)
    ap.add_argument("--start-date", default=None)
    ap.add_argument("--n-stocks", type=int, default=300, help="synthetic only")
    a = ap.parse_args()

    if a.price_only and a.data == "synthetic":
        raise SystemExit("--price-only needs real data (market caps)")
    if a.data == "synthetic":
        from data_synth import make_synthetic_panel
        panel = make_synthetic_panel(a.n_stocks, 0)
    else:
        from data_real import PRICE_FACTORS, build_panel
        panel = build_panel(a.raw_dir, min_coverage=a.min_coverage, top_n_mcap=a.top_n_mcap,
                            market=None if a.market == "ALL" else a.market, price_only=a.price_only)
    if a.start_date:
        panel = panel[panel["date"] >= pd.Timestamp(a.start_date)]
    panel = panel.dropna(subset=["ret_next", "mkt_next"])
    factors = ([c for c in PRICE_FACTORS if c in panel.columns] if a.price_only
               else [c for c in FACTOR_SETS[a.factor_set] if c in panel.columns])
    n = panel.groupby("date").size()
    print(f"{len(panel):,} stock-months, {panel.ticker.nunique()} tickers, {n.min()}-{n.max()} stocks/month, "
          f"{panel['date'].nunique()} months")
    ic = monthly_rank_ic(panel, factors)
    res = summarize(ic)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    ic.to_csv(out / "monthly_ic.csv"); res.to_csv(out / "factor_ic_summary.csv")
    print(res.to_string(float_format=lambda x: f"{x:.3f}"))
    print(f"\nwritten to {out}. With {panel['date'].nunique()} months a mean IC needs roughly |t_nw| > 2 to stand "
          "out; with many factors expect a few to pass by chance.")


if __name__ == "__main__":
    main()

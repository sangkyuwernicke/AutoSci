#!/usr/bin/env python3
"""Where does a model's cross-sectional AUC come from? Remove known factors from its score and re-measure.

  python analyze_auc_sources.py --run results/v14_to2026_top200_feature --out results/v18_auc_sources

For one run (predictions.parquet) and every (model, feature set): the monthly AUC of the score, and the monthly AUC
of the score after removing, month by month and cross-sectionally, the part explained by control sets. Removal is
`factor_ic.add_residuals` (OLS on percentile ranks), the AUC is the mean over months of the within-month AUC for the
run's label. A residual AUC near 0.5 means the controls explain the skill.

Also written: the single-factor monthly AUC of each control (0.5 = none; < 0.5 means LOW values go up) and its mean
rank correlation with each model's score. The factor values come from data_real.build_panel with the same universe
settings as the run (--market / --top-n-mcap / --min-coverage), merged on (date, ticker).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

from data_real import build_panel
from factor_ic import add_residuals

FACTORS = ["VOL_20D", "RET_1M", "RET_3M", "RET_12M", "PBR", "ROE"]
CONTROL_SETS = {
    "vol": ["VOL_20D"], "size": ["lmcap"], "reversal": ["RET_1M", "RET_3M"],
    "vol+size+rev+mom12": ["VOL_20D", "lmcap", "RET_1M", "RET_3M", "RET_12M"],
    "value+quality (PBR, ROE)": ["PBR", "ROE"],
    "ALL: vol+size+rev+mom12 + PBR+ROE": ["VOL_20D", "lmcap", "RET_1M", "RET_3M", "RET_12M", "PBR", "ROE"],
}
MIN_STOCKS = 30


def monthly_auc(df: pd.DataFrame, col: str) -> float:
    a = [roc_auc_score(g["y"], g[col]) for _, g in df.dropna(subset=[col]).groupby("date")
         if g["y"].nunique() == 2 and len(g) > MIN_STOCKS]
    return float(np.mean(a))


def monthly_corr(df: pd.DataFrame, a: str, b: str) -> float:
    c = [spearmanr(g[a], g[b])[0] for _, g in df.dropna(subset=[a, b]).groupby("date") if len(g) > MIN_STOCKS]
    return float(np.mean(c))


def residual_table(pred: pd.DataFrame, models, fsets) -> pd.DataFrame:
    rows = []
    for m in models:
        for fs in fsets:
            g0 = pred[(pred.model == m) & (pred.fset == fs)].reset_index(drop=True)
            for name, ctl in CONTROL_SETS.items():
                ok = g0["score"].notna() & g0[ctl].notna().all(axis=1)
                g = g0[ok].reset_index(drop=True)
                q = add_residuals(g, ["score"], ctl)
                rows.append(dict(model=m, fset=fs, controls=name, rows_used=float(ok.mean()),
                                 auc_score=monthly_auc(g, "score"), auc_residual=monthly_auc(q, "score_RES")))
    return pd.DataFrame(rows)


def single_factor_table(pred: pd.DataFrame, models, fset: str) -> pd.DataFrame:
    base = pred[(pred.model == models[0]) & (pred.fset == fset)]
    rows = []
    for f in FACTORS + ["lmcap"]:
        r = {"factor": f, "auc_alone": monthly_auc(base, f)}
        for m in models:
            r[f"corr_{m}"] = monthly_corr(pred[(pred.model == m) & (pred.fset == fset)], "score", f)
        rows.append(r)
    return pd.DataFrame(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True, help="results dir with predictions.parquet")
    ap.add_argument("--raw-dir", default="data/real")
    ap.add_argument("--market", default="KOSPI")
    ap.add_argument("--top-n-mcap", type=int, default=0)
    ap.add_argument("--min-coverage", type=float, default=0.5)
    ap.add_argument("--fsets", nargs="+", default=["firm"], help="feature sets to decompose (firm / full / gated)")
    ap.add_argument("--out", default="results/v18_auc_sources")
    args = ap.parse_args()

    pred = pd.read_parquet(Path(args.run) / "predictions.parquet")
    pred["date"] = pd.to_datetime(pred["date"])
    pan = build_panel(args.raw_dir, min_coverage=args.min_coverage, top_n_mcap=args.top_n_mcap,
                      market=None if args.market == "ALL" else args.market)
    keep = ["date", "ticker"] + [c for c in FACTORS if c in pan.columns]
    pred = pred.merge(pan[keep], on=["date", "ticker"], how="left")
    pred["lmcap"] = np.log(pred["mcap"])
    models = [m for m in ["logit", "ridge", "dtree", "rf", "xgb", "lgbm", "catboost"] if m in set(pred["model"])]

    res = residual_table(pred, models, args.fsets)
    single = single_factor_table(pred, models, args.fsets[0])
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    res.to_csv(out / "residual_auc.csv", index=False, encoding="utf-8-sig")
    single.to_csv(out / "single_factor_auc_and_corr.csv", index=False, encoding="utf-8-sig")
    fmt = lambda d: d.to_string(index=False, float_format=lambda v: f"{v:.3f}")                    # noqa: E731
    text = "\n".join(["# AUC sources", "", f"run: {args.run}  months: {pred['date'].nunique()}", "",
                      "## Single-factor monthly AUC and rank correlation with each model's score", fmt(single), "",
                      "## Monthly AUC of the score vs of its residual (same rows)", fmt(res), ""])
    (out / "summary.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

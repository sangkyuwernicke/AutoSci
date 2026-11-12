#!/usr/bin/env python3
"""Representative table: firm-factor ML x macro x news sentiment.

  python make_summary_table.py --none results/v15_sent_none_quick_feature \
      --finbert results/v15_sent_finbert_quick_feature --out results/v15_summary

Panel A  2x2 design per model, from the two runs' predictions.parquet (same recomputation as compare_runs.py:
         top-q portfolio, net of cost). Columns: {Firm, Firm+Macro} x {no sentiment, + FinBert}.
         Metrics: mean monthly AUC and net Sharpe. Footer rows pool the models: mean difference per factor
         (macro, sentiment) with a block-bootstrap CI of the model-averaged monthly AUC difference.
Panel B  Single-factor rank IC of the sentiment factors (factor_ic.py outputs), raw and after removing
         RET_1M, RET_3M, VOL_20D, market cap month by month.

The portfolio columns of metrics.csv / report.md are NOT used: in a --quick run (~91 stocks) --top-k 200 makes every
model hold the whole universe. Here the book is re-selected from the stored scores (--top-q: 0.2 = top 20 %, 200 =
top 200 stocks as in the original whole-KOSPI design). The models are read from the data, so a --small-data pair
(logit, lgbm, catboost) works as well as the 7-model one. Original design:
  python make_summary_table.py --none results/v16_fulluniv_sentnone_feature \
      --finbert results/v16_fulluniv_sentfinbert_feature --top-q 200 \
      --ic results/v16_ic_resid_all_finbert_allcontrols="whole KOSPI" --out results/v18_summary_full
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import evaluation as ev

PREFERRED_ORDER = ["logit", "ridge", "dtree", "rf", "xgb", "lgbm", "catboost"]
CONFIGS = {"Firm": ("none", "firm"), "Firm+Macro": ("none", "full"),
           "Firm+Sent": ("finbert", "firm"), "Firm+Macro+Sent": ("finbert", "full")}
SENT = ["SENT_MEAN_1W", "SENT_MEAN_1M", "SENT_MEAN_3M", "SENT_CHG", "SENT_STD_1M", "NEWS_COUNT_1M"]
DEFAULT_IC = ["results/v15_ic_resid_all_finbert_top100=top100", "results/v15_ic_resid_all_finbert_top200=top200"]
SMALL_UNIVERSE = 300      # below this the run is not the original whole-KOSPI design


def models_in(runs: dict[str, pd.DataFrame]) -> list[str]:
    """Models present in every run, in a fixed display order (unknown names sorted after the known ones)."""
    common = set.intersection(*(set(p["model"].unique()) for p in runs.values()))
    return [m for m in PREFERRED_ORDER if m in common] + sorted(common - set(PREFERRED_ORDER))


def describe(runs: dict[str, pd.DataFrame], top_q: float, cost: float) -> str:
    """One paragraph on the setup, derived from the data (universe size, test months, book size)."""
    p = runs["none"]
    n_univ = int(p.groupby("date").ticker.nunique().median())
    book = f"top {int(top_q)} stocks" if top_q >= 1 else f"top {top_q:.0%}"
    txt = (f"{n_univ} stocks per month (median), {p['date'].nunique()} test months "
           f"({p['date'].min():%Y-%m}~{p['date'].max():%Y-%m}), label = next-month direction, "
           f"portfolio = {book} by predicted P(up), equal weight, cost {cost:.2%} x sum|dw|; "
           f"Sharpe = monthly mean/std x sqrt(12), rf = 0. Index rows are price indices without costs; model rows "
           f"are net of cost.")
    if n_univ < SMALL_UNIVERSE:
        txt += (f" Not the original design (whole KOSPI ~650 stocks, hold 200 vs KOSPI200 EW): the universe here is "
                f"the ~{n_univ} largest stocks.")
    return txt


def month_series(pred: pd.DataFrame, top_q: float, cost: float) -> pd.DataFrame:
    """Monthly AUC, Precision@top-q and net return of one (model, feature set)."""
    bt = ev.backtest(pred, top_q, cost)
    return ev.monthly_table(pred, top_q).join(bt[["net", "universe"]])


def sharpe(x: pd.Series) -> float:
    return float(ev.perf_stats(x.dropna())["Sharpe"])


def index_sharpe(run_dir: Path, name: str, months: pd.DatetimeIndex) -> float:
    """Sharpe of an official index series stored by run_experiment.py (monthly returns on the model's decision dates)."""
    s = pd.read_csv(run_dir / name, index_col=0, parse_dates=True).iloc[:, 0].dropna()
    if not set(months) <= set(s.index):
        raise SystemExit(f"{run_dir / name} does not cover all {len(months)} test months")
    return sharpe(s.reindex(months))


def panel_a(runs: dict[str, pd.DataFrame], top_q: float, cost: float, ref_dir: Path | None = None,
            models: list[str] | None = None):
    models = models or models_in(runs)
    cells = {}                                        # (model, config) -> monthly DataFrame
    for cfg, (run, fset) in CONFIGS.items():
        p = runs[run]
        for m in models:
            cells[(m, cfg)] = month_series(p[(p.model == m) & (p.fset == fset)], top_q, cost)
    rows = []
    for m in models:
        r = {"Model": m}
        for cfg in CONFIGS:
            r[f"AUC {cfg}"] = cells[(m, cfg)]["auc"].mean()
        for cfg in CONFIGS:
            r[f"Sharpe {cfg}"] = sharpe(cells[(m, cfg)]["net"])
        rows.append(r)
    tab = pd.DataFrame(rows).set_index("Model")
    tab.loc["Model mean"] = tab.mean()
    sh_cols = [f"Sharpe {c}" for c in CONFIGS]
    base = cells[(models[0], "Firm")]["universe"]     # equal-weight test universe, identical for every model
    tab.loc["EW of test universe (no model, no cost)", sh_cols] = sharpe(base)
    if ref_dir is not None:                           # the pipeline's own benchmarks (data/krx official index files)
        months = base.index
        tab.loc["KOSPI200 EW official (primary benchmark)", sh_cols] = index_sharpe(ref_dir, "kospi200_ew_official_monthly.csv", months)
        tab.loc["KOSPI200 cap-weighted official", sh_cols] = index_sharpe(ref_dir, "kospi200_official_monthly.csv", months)
    return tab, cells


def pooled_effects(cells: dict, n_boot: int, models: list[str]) -> pd.DataFrame:
    """Model-averaged monthly series per configuration -> effect of macro / sentiment with a block-bootstrap CI."""
    auc = {c: pd.concat([cells[(m, c)]["auc"] for m in models], axis=1).mean(axis=1) for c in CONFIGS}
    sh = {c: np.mean([sharpe(cells[(m, c)]["net"]) for m in models]) for c in CONFIGS}
    d_macro = ((auc["Firm+Macro"] - auc["Firm"]) + (auc["Firm+Macro+Sent"] - auc["Firm+Sent"])) / 2
    d_sent = ((auc["Firm+Sent"] - auc["Firm"]) + (auc["Firm+Macro+Sent"] - auc["Firm+Macro"])) / 2
    s_macro = ((sh["Firm+Macro"] - sh["Firm"]) + (sh["Firm+Macro+Sent"] - sh["Firm+Sent"])) / 2
    s_sent = ((sh["Firm+Sent"] - sh["Firm"]) + (sh["Firm+Macro+Sent"] - sh["Firm+Macro"])) / 2
    out = []
    for name, d, ds in (("Macro effect (Firm+Macro - Firm)", d_macro, s_macro),
                        ("Sentiment effect (+FinBert - none)", d_sent, s_sent)):
        b = ev.mean_diff_bootstrap(d, n_boot)
        out.append({"Effect": name, "mean dAUC": d.mean(), "CI lo": b["boot_ci_lo"], "CI hi": b["boot_ci_hi"],
                    "p (one-sided)": b["p_boot"], "mean dSharpe": ds, "n_months": str(int(d.notna().sum()))})
    return pd.DataFrame(out).set_index("Effect")


def panel_b(ic_specs: list[str]) -> pd.DataFrame:
    """`ic_specs`: 'results/<factor_ic run>=<label>' items; each run needs factor_ic_summary.csv with *_RES rows."""
    parsed = [s.rsplit("=", 1) for s in ic_specs]
    rows = []
    for f in SENT:
        r = {"Factor": f}
        for path, label in parsed:
            d = pd.read_csv(Path(path) / "factor_ic_summary.csv", index_col=0)
            res = d.loc[f + "_RES"] if f + "_RES" in d.index else None
            r[f"avg N ({label})"] = f"{d.loc[f, 'avg_n']:.1f}"
            r[f"IC raw ({label})"] = f"{d.loc[f, 'mean_ic']:+.3f} ({d.loc[f, 't_nw']:+.1f})"
            r[f"IC resid ({label})"] = f"{res['mean_ic']:+.3f} ({res['t_nw']:+.1f})" if res is not None else "-"
        rows.append(r)
    return pd.DataFrame(rows).set_index("Factor")


def to_markdown(a: pd.DataFrame, eff: pd.DataFrame, b: pd.DataFrame, meta: str) -> str:
    return "\n".join([
        "# Firm-factor ML x Macro x News sentiment (KR-FinBert-SC)", "", meta, "",
        "## Panel A. Out-of-sample, 2x2 design per model", "",
        a.map(lambda v: "-" if pd.isna(v) else f"{v:.3f}").to_markdown(), "",
        "### Pooled effects (models averaged; CI = circular block bootstrap of the monthly AUC difference)", "",
        eff.to_markdown(floatfmt=".4f"), "",
        "## Panel B. Single-factor rank IC of the sentiment factors, mean IC (Newey-West t)", "",
        "raw = as is; resid = after removing RET_1M, RET_3M, VOL_20D, market cap month by month.", "",
        b.to_markdown(), ""])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--none", required=True, help="run without sentiment (predictions.parquet)")
    ap.add_argument("--finbert", required=True, help="run with --sentiment finbert, same settings")
    ap.add_argument("--out", default="results/v15_summary")
    ap.add_argument("--ic", nargs="+", default=DEFAULT_IC, metavar="DIR=LABEL",
                    help="factor_ic.py output dirs (run with --sentiment finbert --residualize-on ...) for Panel B, "
                         "each as <dir>=<label>")
    ap.add_argument("--top-q", type=float, default=0.2, help="fraction (< 1) or number of stocks held (>= 1, e.g. 200)")
    ap.add_argument("--cost", type=float, default=0.002)
    ap.add_argument("--n-boot", type=int, default=5000)
    args = ap.parse_args()

    runs = {}
    for k in ("none", "finbert"):
        p = pd.read_parquet(Path(getattr(args, k)) / "predictions.parquet")
        p["date"] = pd.to_datetime(p["date"])
        runs[k] = p
    key = ["date", "ticker"]
    y0 = runs["none"].drop_duplicates(key).set_index(key)["y"]
    y1 = runs["finbert"].drop_duplicates(key).set_index(key)["y"]
    if not y0.index.equals(y1.index) or (y0 != y1).any():
        raise SystemExit("the two runs do not cover the same stock-months / labels; rerun with identical settings")

    models = models_in(runs)
    a, cells = panel_a(runs, args.top_q, args.cost, Path(args.none), models)
    eff = pooled_effects(cells, args.n_boot, models)
    b = panel_b(args.ic)
    meta = f"Models: {', '.join(models)}. " + describe(runs, args.top_q, args.cost)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    a.to_csv(out / "panel_a_models.csv", encoding="utf-8-sig")
    eff.to_csv(out / "panel_a_effects.csv", encoding="utf-8-sig")
    b.to_csv(out / "panel_b_ic.csv", encoding="utf-8-sig")
    md = to_markdown(a, eff, b, meta)
    (out / "summary_table.md").write_text(md, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Walk-forward experiment: tune -> predict -> evaluate -> backtest -> H1/H2 tests -> SHAP (H3).

    python run_experiment.py --data synthetic --trials 10 --out results/synth
    python run_experiment.py --data real --raw-dir data/real --trials 50 --out results/real
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

import evaluation as ev
import shap_analysis as sa
from config import FACTOR_SETS, MACRO, MODELS, REGIME_VARS
from features import add_target, cross_sectional_transform
from models import build, score, tune


def parse():
    a = argparse.ArgumentParser()
    a.add_argument("--data", choices=["synthetic", "real"], default="synthetic")
    a.add_argument("--raw-dir", default="data/real")
    a.add_argument("--out", default="results/run")
    a.add_argument("--models", nargs="+", default=MODELS, choices=MODELS)
    a.add_argument("--trials", type=int, default=20, help="Optuna trials per model/fold/feature set")
    a.add_argument("--seed", type=int, default=0)
    a.add_argument("--n-jobs", type=int, default=-1)
    a.add_argument("--n-stocks", type=int, default=300, help="synthetic only")
    a.add_argument("--train-start", type=int, default=2014)
    a.add_argument("--test-start", type=int, default=2022)
    a.add_argument("--test-end", type=int, default=2025)
    a.add_argument("--target-quantile", type=float, default=None,
                   help="y=1 for the top (1-q) share by monthly excess return, e.g. 0.8 -> top 20%% (1:4); "
                        "exclusive with --target-margin")
    a.add_argument("--target-margin", type=float, default=0.0,
                   help="y=1 iff R_i - R_m > margin (e.g. 0.03 for a rarer positive class)")
    a.add_argument("--factor-set", choices=list(FACTOR_SETS), default="base",
                   help="base = plan's 17 factors; extended adds momentum/R&D/capex/forward-looking factors")
    a.add_argument("--min-mcap-pct", type=float, default=0.0, help="real data: drop the smallest x%% by market cap each month")
    a.add_argument("--min-coverage", type=float, default=0.5,
                   help="real data: drop stock-months with < this share of the 13 statement-based factors")
    a.add_argument("--scale", choices=["quantile", "zscore"], default="quantile")
    a.add_argument("--top-q", type=float, default=0.2)
    a.add_argument("--cost", type=float, default=0.002, help="applied to sum|dw| each rebalance")
    a.add_argument("--shap-model", default="lgbm", choices=["rf", "xgb", "lgbm", "catboost"])
    a.add_argument("--n-perm", type=int, default=2000)
    a.add_argument("--n-inter", type=int, default=2000, help="rows per fold for SHAP interactions")
    a.add_argument("--top-n-mcap", type=int, default=0,
                   help="real data: keep only the N largest stocks by market cap each month (0 = all)")
    a.add_argument("--quick", action="store_true",
                   help="fast profile: 100 stocks, train 2019+, test 2023-2025, 15 Optuna trials, "
                        "lighter SHAP. Explicit flags still override.")
    q, _ = a.parse_known_args()
    if q.quick:
        a.set_defaults(n_stocks=100, top_n_mcap=100, train_start=2019, test_start=2023, test_end=2025,
                       trials=15, n_perm=500, n_inter=1000)
    return a.parse_args()


def load(args):
    if args.data == "synthetic":
        from data_synth import make_synthetic_panel
        return make_synthetic_panel(args.n_stocks, args.seed)
    from data_real import build_panel
    return build_panel(args.raw_dir, min_mcap_pct=args.min_mcap_pct, min_coverage=args.min_coverage,
                       top_n_mcap=args.top_n_mcap)


def fmt(df, nd=4):
    return df.to_string(float_format=lambda x: f"{x:.{nd}f}")


def main():
    args = parse()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    raw = load(args)
    firm_cols = [c for c in FACTOR_SETS[args.factor_set] if c in raw.columns]
    missing = [c for c in FACTOR_SETS[args.factor_set] if c not in raw.columns]
    if missing:
        print(f"WARNING: factors not available in this panel and skipped: {missing}")
    feature_sets = {"full": firm_cols + MACRO, "firm": firm_cols}
    if args.data == "real":
        from data_quality import quality_report
        quality_report(raw, firm_cols + MACRO).to_csv(out / "data_quality.csv")
    panel = add_target(raw, args.target_margin, args.target_quantile)
    panel = panel[panel.label_year >= args.train_start]
    panel = cross_sectional_transform(panel, firm_cols, method=args.scale)
    print(f"panel: {len(panel):,} rows, {panel.ticker.nunique()} tickers, "
          f"label years {panel.label_year.min()}-{panel.label_year.max()}, "
          f"positive rate {panel.y.mean():.3f}")

    # ---- walk-forward: for test year Y tune on [start, Y-2] -> validate Y-1 -> refit [start, Y-1] -> test Y
    # Folds are keyed on the year of the *label* month (t+1), so no training label is realised after
    # the first test decision date.
    preds, best, shap_parts, inter_parts = [], {}, [], []
    for Y in range(args.test_start, args.test_end + 1):
        tr = panel[panel.label_year <= Y - 2]
        va = panel[panel.label_year == Y - 1]
        trva = panel[panel.label_year <= Y - 1]
        te = panel[panel.label_year == Y]
        if te.empty:
            continue
        print(f"\n=== test {Y}: train {len(tr):,} / val {len(va):,} / test {len(te):,}")
        for fset, cols in feature_sets.items():
            for name in args.models:
                t1 = time.time()
                bp, bv = tune(name, tr[cols], tr.y, va[cols], va.y, args.trials, args.seed, args.n_jobs)
                model = build(name, bp, args.seed, args.n_jobs).fit(trva[cols], trva.y)
                s = score(model, te[cols])
                preds.append(te[["date", "ticker", "y", "ret_next", "mkt_next"]].assign(
                    score=s, model=name, fset=fset, test_year=Y))
                best[f"{Y}/{fset}/{name}"] = dict(params=bp, val_auc=bv)
                print(f"  {fset:4s} {name:8s} val AUC {bv:.4f}  test AUC {roc_auc_score(te.y, s):.4f}"
                      f"  ({time.time() - t1:.0f}s)")

                if fset == "full" and name == args.shap_model:
                    sv, idx, iv = sa.fold_shap(model, te[cols], args.n_inter, args.seed)
                    shap_parts.append((te[["date"] + cols], sv))
                    inter_parts.append((iv, te[cols].iloc[idx]))

    pred = pd.concat(preds, ignore_index=True)
    pred.to_parquet(out / "predictions.parquet")
    (out / "best_params.json").write_text(json.dumps(best, indent=1, default=float))

    # ---- prediction metrics + backtest
    rows, bt = [], {}
    for (name, fset), g in pred.groupby(["model", "fset"]):
        r = {"model": name, "fset": fset, **ev.prediction_metrics(g, args.top_q)}
        b = ev.backtest(g, args.top_q, args.cost)
        bt[(name, fset)] = b
        r.update(ev.perf_stats(b.net, b.bench, b.turnover[~b["first"]]))
        rows.append(r)
    ref = next(iter(bt.values()))
    bench = pd.DataFrame([{"model": "MARKET", "fset": "-", **ev.perf_stats(ref.bench)},
                          {"model": "EW_UNIVERSE", "fset": "-", **ev.perf_stats(ref.universe, ref.bench)}])
    res = pd.concat([pd.DataFrame(rows), bench], ignore_index=True)
    res.to_csv(out / "metrics.csv", index=False)
    pd.concat({f"{k[0]}/{k[1]}": v for k, v in bt.items()}, names=["strategy"]).to_csv(out / "backtest_monthly.csv")

    # ---- H1: integrated (full) vs firm-only
    h1 = []
    for name in args.models:
        a = ev.monthly_table(pred[(pred.model == name) & (pred.fset == "full")], args.top_q)
        b = ev.monthly_table(pred[(pred.model == name) & (pred.fset == "firm")], args.top_q)
        for metric in ("auc", "prec_k"):
            h1.append({"model": name, "metric": metric, **ev.paired_tests(a[metric], b[metric])})
    h1 = pd.DataFrame(h1)
    h1.to_csv(out / "h1_macro_vs_firm.csv", index=False)

    # ---- H2: tree ensembles vs logistic regression (net monthly returns, full features)
    h2 = []
    if "logit" in args.models:
        base = bt[("logit", "full")].net
        for name in args.models:
            if name in ("xgb", "lgbm", "rf", "catboost"):
                h2.append({"model": name, "vs": "logit", **ev.sharpe_diff_bootstrap(bt[(name, "full")].net, base)})
    h2 = pd.DataFrame(h2)
    h2.to_csv(out / "h2_sharpe_vs_logit.csv", index=False)

    # ---- H3: SHAP by macro regime + interactions
    h3_text = ""
    if shap_parts:
        X_all = pd.concat([p[0] for p in shap_parts]); sv_all = pd.concat([p[1] for p in shap_parts])
        # Regime = macro level above/below the median over the test months. This is an ex-post
        # description of the OOS period (not an input to any model), and it guarantees both regimes
        # are populated even when the test era sits entirely above the training-era median.
        monthly = X_all.groupby("date")[list(REGIME_VARS)].first()
        flags = pd.DataFrame({v: X_all["date"].map(sa.regime_flags(monthly[v])).astype(bool) for v in REGIME_VARS})
        sv_all.to_parquet(out / "shap_values.parquet")
        sa.plot_summary(sv_all, X_all[feature_sets["full"]], out / "shap_summary.png")
        imp = sv_all.abs().mean().sort_values(ascending=False)
        imp.to_csv(out / "shap_global_importance.csv")
        h3_text += "Global mean|SHAP| (top 10):\n" + fmt(imp.head(10).to_frame("mean_abs_shap")) + "\n"
        for var, tag in REGIME_VARS.items():
            tab, summ = sa.regime_analysis(sv_all[firm_cols], X_all[firm_cols], X_all["date"],
                                           flags[var], args.n_perm, args.seed)
            tab.sort_values("imp_high", ascending=False).to_csv(out / f"shap_regime_{tag}.csv")
            sa.plot_regime_bars(tab, var, out / f"shap_regime_{tag}.png")
            h3_text += (f"\n[{var} high vs low] rank corr={summ['spearman_rank_corr']:.3f}, "
                        f"permutation p={summ['p_perm']:.4f}, months high/low="
                        f"{summ['n_months_high']}/{summ['n_months_low']}, "
                        f"sign flips={int(tab.sign_flip.sum())}/{len(tab)}\n"
                        + fmt(tab.sort_values("imp_high", ascending=False).head(8)) + "\n")
        iv = np.concatenate([p[0] for p in inter_parts]); Xi = pd.concat([p[1] for p in inter_parts])
        mat = sa.interaction_matrix(iv, feature_sets["full"], firm_cols)
        mat.to_csv(out / "shap_interaction_macro_x_firm.csv")
        sa.plot_interaction_heatmap(mat, out / "shap_interaction_heatmap.png")
        sa.plot_pair_scatter(iv, Xi, "PBR", "BASE_RATE", out / "shap_interaction_PBR_x_BASE_RATE.png")
        top = mat.stack().sort_values(ascending=False).head(8)
        h3_text += "\nTop macro x firm interactions (mean|phi_ij|*2):\n" + fmt(top.to_frame("value")) + "\n"

    # ---- report
    cols = ["model", "fset", "auc_pooled", "auc_monthly", "pr_auc", "prec_at_k", "base_rate",
            "CAGR", "Sharpe", "MDD", "WinRate_vs_bm", "Turnover"]
    rep = ["# Experiment report", f"data={args.data} trials={args.trials} cost={args.cost} top_q={args.top_q} "
           f"margin={args.target_margin} quantile={args.target_quantile}", "", "## Prediction + backtest (net of costs)", "```",
           fmt(res[cols].fillna(np.nan)), "```", "", "## H1: full (firm+macro) minus firm-only, paired by month",
           "```", fmt(h1, 5), "```", "", "## H2: Sharpe(model) - Sharpe(logit), block bootstrap", "```",
           fmt(h2) if len(h2) else "logit not run", "```", "", "## H3: SHAP", "```", h3_text, "```"]
    (out / "report.md").write_text("\n".join(rep))
    print("\n".join(rep))
    print(f"\ndone in {time.time() - t0:.0f}s -> {out}")


if __name__ == "__main__":
    main()

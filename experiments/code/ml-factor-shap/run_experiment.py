"""Walk-forward experiment: tune -> predict -> evaluate -> backtest -> H1/H2 tests -> SHAP/gating (H3).

    # --- feature mode (default): macro as direct input features
    python run_experiment.py --data synthetic --trials 10 --out results/synth
    python run_experiment.py --data real --raw-dir data/real --trials 50 --out results/real

    # --- gating mode: macro governs per-factor weights via RegimeGatedScorer
    python run_experiment.py --data synthetic --macro-role gating --trials 15 --out results/synth_gated
    python run_experiment.py --data real --raw-dir data/real --macro-role gating --trials 50 --out results/real_gated

Macro-role semantics
────────────────────
  feature (default) : macro vars enter the model as ordinary input features alongside firm
                      factors. The standard "full" vs "firm-only" feature-set comparison
                      is run to test H1 (does adding macro help?).

  gating            : macro vars feed only the gating network of RegimeGatedScorer, which
                      produces soft regime weights α_k(m_t). Firm factors z_i are scored by
                      expert k with weight β_k; the final score is Σ_k α_k(m_t)·p_k(z_i).
                      H1 compares RegimeGatedScorer against each firm-only model.
                      Outputs include gating_factor_weights.csv and regime centroid plots.
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
from features import add_target, impute_ffill, cross_sectional_transform, macro_to_regime
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
    a.add_argument("--train-start", type=int, default=2021)
    a.add_argument("--test-start", type=int, default=2022)
    a.add_argument("--test-end", type=int, default=2025)
    a.add_argument("--target", choices=["direction", "excess"], default="direction",
                   help="direction (default): y=1 iff the stock's own next-month return > 0, then hold the top-q by "
                        "predicted P(up). excess: y=1 iff beating the market (relative label, legacy)")
    a.add_argument("--max-missing", type=float, default=0.3,
                   help="drop factors still missing in more than this share of rows after forward-fill")
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
    a.add_argument("--top-q", type=float, default=0.2, help="fraction held; used only when --top-k is 0")
    a.add_argument("--kospi200-csv", default="data/krx/index_kospi200.csv",
                   help="official KOSPI200 price index (KRX download: 일자,종가); added to the benchmarks if present")
    a.add_argument("--kospi200-ew-csv", default="data/krx/index_kospi200_ew.csv",
                   help="official KOSPI200 equal-weight price index (KRX download: 일자,종가); added to the benchmarks if present")
    a.add_argument("--tune-metric", choices=["monthly", "pooled"], default="monthly",
                   help="Optuna objective on the validation year: monthly (default) = mean of the per-month AUC, i.e. "
                        "cross-sectional ordering only, as the top-K portfolio uses it; pooled = one AUC over all "
                        "validation rows, which also rewards guessing each month's market direction from macro")
    a.add_argument("--top-k", type=int, default=200,
                   help="number of stocks held (top-k by predicted P(up)); 0 = use --top-q instead")
    a.add_argument("--cost", type=float, default=0.002, help="applied to sum|dw| each rebalance")
    a.add_argument("--shap-model", default="lgbm", choices=["rf", "xgb", "lgbm", "catboost"])
    a.add_argument("--n-perm", type=int, default=2000)
    a.add_argument("--n-inter", type=int, default=2000, help="rows per fold for SHAP interactions")
    a.add_argument("--top-n-mcap", type=int, default=0,
                   help="real data: keep only the N largest stocks by market cap each month (0 = all)")
    a.add_argument("--market", choices=["ALL", "KOSPI", "KOSDAQ"], default="ALL",
                   help="real data: restrict the universe and the benchmark index to one market")
    a.add_argument("--start-date", default=None, help="drop feature dates before this (YYYY-MM-DD)")
    a.add_argument("--small-data", action="store_true",
                   help="few thousand training rows: shallow/regularised search space and, unless --models is "
                        "given, only logit, lgbm and catboost (fewer comparisons)")
    a.add_argument("--macro-mode", choices=["raw", "regime"], default="raw",
                   help="regime: macro levels -> 1/0/0.5 vs their expanding median (no look-ahead), so trees "
                        "cannot memorise which month a row belongs to")
    a.add_argument("--macro-role", choices=["feature", "gating"], default="feature",
                   help="feature (default): macro vars are direct model inputs alongside firm factors. "
                        "gating: macro vars only control per-factor weights via RegimeGatedScorer — "
                        "they never enter directly as predictors. H1 compares gated vs firm-only.")
    a.add_argument("--quick", action="store_true",
                   help="fast profile: KOSPI top-100, data from 2020-01-02, train 2020+, test 2023-2025, 15 Optuna trials, "
                        "lighter SHAP. Explicit flags still override.")
    q, _ = a.parse_known_args()
    if q.small_data:
        a.set_defaults(models=["logit", "lgbm", "catboost"])
    if q.quick:
        a.set_defaults(n_stocks=100, top_n_mcap=100, market="KOSPI", start_date="2021-01-01",
                       train_start=2021, test_start=2023, test_end=2025,
                       trials=15, n_perm=500, n_inter=1000)
    return a.parse_args()


FSET_LABELS = {"firm": "Firm-only", "full": "Firm+Macro", "gated": "Firm+Macro (gating)"}   # report display only


def load(args):
    if args.data == "synthetic":
        from data_synth import make_synthetic_panel
        return make_synthetic_panel(args.n_stocks, args.seed)
    from data_real import build_panel
    return build_panel(args.raw_dir, min_mcap_pct=args.min_mcap_pct, min_coverage=args.min_coverage,
                       top_n_mcap=args.top_n_mcap,
                       market=None if args.market == "ALL" else args.market)


def fmt(df, nd=4):
    return df.to_string(float_format=lambda x: f"{x:.{nd}f}")


def main():
    args = parse()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    raw = load(args)
    if args.start_date:
        raw = raw[raw["date"] >= pd.Timestamp(args.start_date)]

    firm_cols = [c for c in FACTOR_SETS[args.factor_set] if c in raw.columns]
    missing = [c for c in FACTOR_SETS[args.factor_set] if c not in raw.columns]
    if missing:
        print(f"WARNING: factors not available in this panel and skipped: {missing}")

    # Macro columns actually available in this panel
    macro_cols_avail = [c for c in MACRO if c in raw.columns]

    if args.data == "real":
        from data_quality import quality_report
        quality_report(raw, firm_cols + macro_cols_avail).to_csv(out / "data_quality.csv")

    raw, kept, imp_rep = impute_ffill(raw, firm_cols, args.max_missing)
    imp_rep.to_csv(out / "imputation_report.csv")
    dropped = [c for c in firm_cols if c not in kept]
    if dropped:
        print(f"dropped factors (> {args.max_missing:.0%} missing after ffill): {dropped}")
    firm_cols = kept
    print("residual missing share (median-imputed after rank transform): "
          f"{raw[firm_cols].isna().mean().mean():.3%}")
    panel = add_target(raw, args.target_margin, args.target_quantile,
                       direction=(args.target == "direction" and args.target_quantile is None
                                  and args.target_margin == 0.0))
    panel = panel[panel.label_year >= args.train_start]
    if args.macro_mode == "regime":
        panel = macro_to_regime(panel, macro_cols_avail)
    regime_src = {v: (f"{v}_RAW" if args.macro_mode == "regime" else v) for v in REGIME_VARS}
    panel = cross_sectional_transform(panel, firm_cols, method=args.scale)
    print(f"panel: {len(panel):,} rows, {panel.ticker.nunique()} tickers, "
          f"label years {panel.label_year.min()}-{panel.label_year.max()}, "
          f"positive rate {panel.y.mean():.3f}")

    # ── Feature-set and model routing based on --macro-role ──────────────────
    # feature mode: macro as direct inputs; two feature sets compared per model.
    # gating mode:  macro only feeds RegimeGatedScorer gating network.
    #               "gated" fset -> macro_gated model only
    #               "firm"  fset -> all args.models (no macro), for H1 baseline
    if args.macro_role == "gating":
        feature_sets = {
            "gated": firm_cols + macro_cols_avail,
            "firm":  firm_cols,
        }
        fset_models = {
            "gated": ["macro_gated"],
            "firm":  args.models,
        }
    else:   # "feature"
        feature_sets = {
            "full": firm_cols + macro_cols_avail,
            "firm": firm_cols,
        }
        fset_models = {
            "full": args.models,
            "firm": args.models,
        }

    # ── Walk-forward loop ─────────────────────────────────────────────────────
    # Folds are keyed on the year of the *label* month (t+1), so no training label
    # is realised after the first test decision date.
    preds, best, shap_parts, inter_parts, gating_parts = [], {}, [], [], []

    for Y in range(args.test_start, args.test_end + 1):
        tr   = panel[panel.label_year <= Y - 2]
        va   = panel[panel.label_year == Y - 1]
        trva = panel[panel.label_year <= Y - 1]
        te   = panel[panel.label_year == Y]
        if te.empty:
            continue
        print(f"\n=== test {Y}: train {len(tr):,} / val {len(va):,} / test {len(te):,}")

        for fset, cols in feature_sets.items():
            for name in fset_models[fset]:
                # Gating model needs explicit column lists; others leave as None
                fc = firm_cols         if name == "macro_gated" else None
                mc = macro_cols_avail  if name == "macro_gated" else None

                t1 = time.time()
                bp, bv = tune(name, tr[cols], tr.y, va[cols], va.y,
                              args.trials, args.seed, args.n_jobs,
                              small=args.small_data, firm_cols=fc, macro_cols=mc,
                              groups_va=va["date"] if args.tune_metric == "monthly" else None)
                model = build(name, bp, args.seed, args.n_jobs, fc, mc).fit(trva[cols], trva.y)
                s = score(model, te[cols])
                preds.append(te[["date", "ticker", "y", "ret_next", "mkt_next"] + (["mcap"] if "mcap" in te else [])].assign(
                    score=s, model=name, fset=fset, test_year=Y))
                best[f"{Y}/{fset}/{name}"] = dict(params=bp, val_auc=bv)
                print(f"  {fset:5s} {name:12s} val AUC {bv:.4f}  "
                      f"test AUC {roc_auc_score(te.y, s):.4f}  ({time.time() - t1:.0f}s)")

                # --- SHAP (tree models on the richer feature set)
                shap_trigger = (
                    (args.macro_role == "feature" and fset == "full" and name == args.shap_model) or
                    (args.macro_role == "gating"  and fset == "firm" and name == args.shap_model)
                )
                if shap_trigger:
                    sv, idx, iv = sa.fold_shap(model, te[cols], args.n_inter, args.seed)
                    shap_parts.append((
                        te[["date"] + cols + [c for c in regime_src.values() if c not in cols]], sv
                    ))
                    inter_parts.append((iv, te[cols].iloc[idx]))

                # --- Gating weight export (RegimeGatedScorer only)
                if name == "macro_gated":
                    gw = sa.fold_gating_weights(
                        model,
                        te[firm_cols + macro_cols_avail],
                        macro_cols_avail,
                        te["date"],
                    )
                    gating_parts.append((Y, gw, model))

    pred = pd.concat(preds, ignore_index=True)
    pred.to_parquet(out / "predictions.parquet")
    (out / "best_params.json").write_text(json.dumps(best, indent=1, default=float))

    # ── Prediction metrics + backtest ─────────────────────────────────────────
    if args.top_k:
        args.top_q = float(args.top_k)                       # evaluation.select_k reads >= 1 as a count
    months = pd.DatetimeIndex(sorted(pred["date"].unique()))
    # Primary benchmark: official KOSPI200 equal-weight (same weighting as the model portfolios); falls back to the
    # cap-weighted market index of the universe when the KRX file is absent. WinRate_vs_bm / Excess_mo use it.
    ew = off = None
    if Path(args.kospi200_ew_csv).exists():
        ew = ev.index_monthly_return(args.kospi200_ew_csv, months)
        ew.rename("kospi200_ew_official").to_csv(out / "kospi200_ew_official_monthly.csv")
    if Path(args.kospi200_csv).exists():
        off = ev.index_monthly_return(args.kospi200_csv, months)
        off.rename("kospi200_official").to_csv(out / "kospi200_official_monthly.csv")
    primary_name = "KOSPI200_EW_OFFICIAL" if ew is not None else "MARKET"
    rows, bt = [], {}
    for (name, fset), g in pred.groupby(["model", "fset"]):
        r = {"model": name, "fset": fset, **ev.prediction_metrics(g, args.top_q)}
        b = ev.backtest(g, args.top_q, args.cost)
        pb = ew if ew is not None else b.bench
        b["bench_primary"] = pb.reindex(b.index)
        bt[(name, fset)] = b
        r.update(ev.perf_stats(b.net, pb, b.turnover[~b["first"]]))
        rows.append(r)
    ref = next(iter(bt.values()))
    pb = ew if ew is not None else ref.bench
    print(f"primary benchmark: {primary_name}")
    bench = pd.DataFrame([{"model": "MARKET",      "fset": "-", **ev.perf_stats(ref.bench, pb)},
                          {"model": "EW_UNIVERSE", "fset": "-", **ev.perf_stats(ref.universe, pb)}])
    if off is not None:                                      # official KOSPI200 (cap-weighted) price index
        bench = pd.concat([bench, pd.DataFrame([{"model": "KOSPI200_OFFICIAL", "fset": "-",
                                                 **ev.perf_stats(off, pb)}])], ignore_index=True)
    if ew is not None:                                       # official KOSPI200 equal-weight price index (primary)
        bench = pd.concat([bench, pd.DataFrame([{"model": "KOSPI200_EW_OFFICIAL", "fset": "-",
                                                 **ev.perf_stats(ew, pb)}])], ignore_index=True)
    if "mcap" in pred:                                       # KOSPI200 proxy (top-200 by market cap, cap-weighted)
        k200 = ev.cap_weighted_top(pred.drop_duplicates(["date", "ticker"]), 200).reindex(ref.index)
        bench = pd.concat([bench, pd.DataFrame([{"model": "KOSPI200_PROXY", "fset": "-",
                                                 **ev.perf_stats(k200, pb)}])], ignore_index=True)
    res = pd.concat([pd.DataFrame(rows), bench], ignore_index=True)
    res.to_csv(out / "metrics.csv", index=False)
    pd.concat({f"{k[0]}/{k[1]}": v for k, v in bt.items()}, names=["strategy"]).to_csv(out / "backtest_monthly.csv")

    # ── H1: does macro information improve prediction? ────────────────────────
    h1 = []
    if args.macro_role == "gating":
        # H1 (gating): RegimeGatedScorer vs each firm-only model
        gated_pred = pred[(pred.model == "macro_gated") & (pred.fset == "gated")]
        a_tab = ev.monthly_table(gated_pred, args.top_q)
        for name in args.models:
            firm_pred = pred[(pred.model == name) & (pred.fset == "firm")]
            if firm_pred.empty:
                continue
            b_tab = ev.monthly_table(firm_pred, args.top_q)
            common = a_tab.index.intersection(b_tab.index)
            for metric in ("auc", "prec_k"):
                r = ev.paired_tests(a_tab.loc[common, metric], b_tab.loc[common, metric])
                r.update(ev.mean_diff_bootstrap(
                    a_tab.loc[common, metric] - b_tab.loc[common, metric]))
                h1.append({"macro_gated_vs": name, "metric": metric, **r})
        h1_csv = "h1_gated_vs_firm.csv"
        h1_title = "## H1: macro_gated vs firm-only models (paired by month)"
    else:
        # H1 (feature): integrated (full) vs firm-only, same model
        for name in args.models:
            a = ev.monthly_table(pred[(pred.model == name) & (pred.fset == "full")], args.top_q)
            b = ev.monthly_table(pred[(pred.model == name) & (pred.fset == "firm")], args.top_q)
            for metric in ("auc", "prec_k"):
                r = ev.paired_tests(a[metric], b[metric])
                r.update(ev.mean_diff_bootstrap(a[metric] - b[metric]))
                h1.append({"model": name, "metric": metric, **r})
        h1_csv = "h1_macro_vs_firm.csv"
        h1_title = "## H1: full (firm+macro) minus firm-only, paired by month"

    h1 = pd.DataFrame(h1)
    if len(h1):
        h1["p_holm"] = ev.holm_adjust(h1["p_ttest"])
    h1.to_csv(out / h1_csv, index=False)

    # ── H2: tree ensembles vs logistic regression ─────────────────────────────
    h2 = []
    if "logit" in args.models:
        logit_fset = "firm" if args.macro_role == "gating" else "full"
        if ("logit", logit_fset) in bt:
            base_net = bt[("logit", logit_fset)].net
            for name in args.models:
                if name in ("xgb", "lgbm", "rf", "catboost"):
                    cmp_fset = "firm" if args.macro_role == "gating" else "full"
                    if (name, cmp_fset) in bt:
                        h2.append({"model": name, "vs": "logit",
                                   **ev.sharpe_diff_bootstrap(bt[(name, cmp_fset)].net, base_net)})
    h2 = pd.DataFrame(h2)
    h2.to_csv(out / "h2_sharpe_vs_logit.csv", index=False)

    # ── H3: SHAP regime analysis + gating weight export ──────────────────────
    h3_text = ""

    # --- H3a: SHAP on tree model (feature mode or firm-only in gating mode)
    if shap_parts:
        X_all = pd.concat([p[0] for p in shap_parts])
        sv_all = pd.concat([p[1] for p in shap_parts])
        # Ex-post regime description over the OOS test months (not a model input)
        monthly = X_all.groupby("date")[list(regime_src.values())].first()
        flags = pd.DataFrame({
            v: X_all["date"].map(sa.regime_flags(monthly[regime_src[v]])).astype(bool)
            for v in REGIME_VARS
        })
        shap_cols = feature_sets.get("full", feature_sets.get("firm", firm_cols))
        sv_all.to_parquet(out / "shap_values.parquet")
        sa.plot_summary(sv_all, X_all[shap_cols], out / "shap_summary.png")
        imp = sv_all.abs().mean().sort_values(ascending=False)
        imp.to_csv(out / "shap_global_importance.csv")
        h3_text += "Global mean|SHAP| (top 10):\n" + fmt(imp.head(10).to_frame("mean_abs_shap")) + "\n"
        for var, tag in REGIME_VARS.items():
            sv_firm = sv_all[[c for c in firm_cols if c in sv_all.columns]]
            X_firm  = X_all[[c for c in firm_cols if c in X_all.columns]]
            tab, summ = sa.regime_analysis(sv_firm, X_firm, X_all["date"],
                                           flags[var], args.n_perm, args.seed)
            tab.sort_values("imp_high", ascending=False).to_csv(out / f"shap_regime_{tag}.csv")
            sa.plot_regime_bars(tab, var, out / f"shap_regime_{tag}.png")
            h3_text += (f"\n[{var} high vs low] rank corr={summ['spearman_rank_corr']:.3f}, "
                        f"permutation p={summ['p_perm']:.4f}, months high/low="
                        f"{summ['n_months_high']}/{summ['n_months_low']}, "
                        f"sign flips={int(tab.sign_flip.sum())}/{len(tab)}\n"
                        + fmt(tab.sort_values("imp_high", ascending=False).head(8)) + "\n")
        if args.macro_role == "feature":
            # macro x firm SHAP interactions only make sense when macro is in the feature set
            iv = np.concatenate([p[0] for p in inter_parts])
            Xi = pd.concat([p[1] for p in inter_parts])
            mat = sa.interaction_matrix(iv, shap_cols, firm_cols)
            mat.to_csv(out / "shap_interaction_macro_x_firm.csv")
            sa.plot_interaction_heatmap(mat, out / "shap_interaction_heatmap.png")
            if "PBR" in firm_cols and "BASE_RATE" in macro_cols_avail:
                sa.plot_pair_scatter(iv, Xi, "PBR", "BASE_RATE",
                                     out / "shap_interaction_PBR_x_BASE_RATE.png")
            top = mat.stack().sort_values(ascending=False).head(8)
            h3_text += "\nTop macro x firm interactions (mean|phi_ij|*2):\n" + fmt(top.to_frame("value")) + "\n"

    # --- H3b: Gating weight analysis (macro_gated model)
    if gating_parts:
        all_gw = pd.concat([gw for (_, gw, _) in gating_parts]).sort_index()
        all_gw.to_csv(out / "gating_factor_weights.csv")
        monthly_macro_panel = panel.groupby("date")[macro_cols_avail].first()
        sa.plot_gating_weights(all_gw, monthly_macro_panel,
                               out / "gating_weights_time.png")
        last_model = gating_parts[-1][2]
        sa.plot_regime_centroids(last_model, out / "gating_regime_centroids.png")
        h3_text += "\n[Macro-Gated Mode] Factor weight time series -> gating_factor_weights.csv\n"
        h3_text += "Regime centroids (last test fold):\n"
        h3_text += fmt(last_model.regime_centroids_df()) + "\n"
        h3_text += "\nFactor weights at first/last test month:\n"
        if len(all_gw) >= 2:
            h3_text += fmt(all_gw.iloc[[0, -1]]) + "\n"

    # ── Resolving-power note ──────────────────────────────────────────────────
    one = pred[(pred["model"] == pred["model"].iloc[0]) & (pred["fset"] == pred["fset"].iloc[0])]
    n_med = one.groupby("date").size().median()
    n_mon = one["date"].nunique()
    br = one["y"].mean()
    se = np.sqrt((n_med + 1) / (12 * n_med * br * n_med * (1 - br))) / np.sqrt(n_mon)
    power_note = (f"{n_mon} test months x ~{int(n_med)} stocks, positive rate {br:.2f}: the mean monthly AUC of a "
                  f"model with no skill has s.e. ~{se:.3f}; AUC gaps below ~{2.8 * se:.3f} (80% power) cannot be "
                  f"told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.")

    # ── Report ────────────────────────────────────────────────────────────────
    report_cols = [c for c in ["model", "fset", "auc_pooled", "auc_monthly", "pr_auc", "prec_at_k",
                               "base_rate", "CAGR", "Sharpe", "MDD", "WinRate_vs_bm", "Excess_mo", "t_excess",
                               "Turnover"]
                   if c in res.columns]
    rep = [
        "# Experiment report",
        f"data={args.data} trials={args.trials} cost={args.cost} top_q={args.top_q} (>=1: number of stocks) "
        f"target={args.target} margin={args.target_margin} quantile={args.target_quantile}",
        f"primary benchmark = {primary_name} (WinRate_vs_bm, Excess_mo [mean monthly excess] and t_excess are measured "
        "against it)",
        "",
        "## Prediction + backtest (net of costs)", "```",
        fmt(res[report_cols].fillna(np.nan).assign(fset=lambda d: d["fset"].replace(FSET_LABELS))), "```", "",
        "fset: Firm-only = firm characteristics only; Firm+Macro = firm characteristics and macro variables as direct "
        "inputs; Firm+Macro (gating) = macro variables only set the factor weights (stored as firm / full / gated in "
        "metrics.csv).", "",
        "## Resolving power", power_note, "",
        f"settings: small_data={args.small_data} macro_mode={args.macro_mode} "
        f"macro_role={args.macro_role} factor_set={args.factor_set} "
        f"market={args.market} top_n_mcap={args.top_n_mcap}", "",
        h1_title, "```", fmt(h1, 5), "```", "",
        "## H2: Sharpe(model) - Sharpe(logit), block bootstrap", "```",
        fmt(h2) if len(h2) else "logit not run", "```", "",
        "## H3: SHAP / Gating analysis", "```", h3_text, "```",
    ]
    (out / "report.md").write_text("\n".join(rep))
    print("\n".join(rep))
    print(f"\ndone in {time.time() - t0:.0f}s -> {out}")


if __name__ == "__main__":
    main()

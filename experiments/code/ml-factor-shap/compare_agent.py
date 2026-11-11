"""Score the agent's decisions against the ML models on the *same* stock-months.

    python compare_agent.py --agent results/agents/run1 --ml-run results/q_base --ml-fset firm \
        --llm-cutoff 2025-06 --out results/agents/run1_vs_ml

Outputs per model: monthly AUC, Precision@K, base rate, net Sharpe of the equal-weight top-K portfolio, plus paired
monthly differences (agent minus ML) with a block-bootstrap interval. `--llm-cutoff YYYY-MM` is the end of the LLM's
training data: decisions dated before it may reflect memorised outcomes, so metrics are also shown separately for
dates before and after the cutoff -- only the post-cutoff block is free of that look-ahead.
The agent row also gets a permutation baseline (its scores shuffled within each month): with ~20 stocks the AUC an
uninformed rater gets by luck is wide, so compare against `auc_null_p95` rather than 0.5. The top-20 % portfolio holds
only ~4 names: read Sharpe as anecdotal.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import evaluation as ev


def metrics_for(df, top_q, cost):
    r = ev.prediction_metrics(df, top_q)
    b = ev.backtest(df, top_q, cost)
    r.update(ev.perf_stats(b.net, b.bench, b.turnover[~b["first"]]))
    return r, b


def null_test(df, top_q, n_perm, seed=0):
    """Permutation test: shuffle the scores across the stocks of each month, recompute mean monthly AUC and
    Precision@K. The shuffled values are what a rater with no information produces on exactly this sample, so the
    spread of that null (not a textbook s.e.) says how much AUC an uninformed agent gets by luck here."""
    rng = np.random.default_rng(seed)
    obs = ev.monthly_table(df, top_q)[["auc", "prec_k"]].mean()
    null = np.empty((n_perm, 2))
    work = df[["date", "ticker", "y", "ret_next", "mkt_next", "score"]].copy()
    groups = [ix for _, ix in work.groupby("date").indices.items()]
    base = work["score"].to_numpy()
    for i in range(n_perm):
        s = base.copy()
        for ix in groups:
            s[ix] = rng.permutation(s[ix])
        work["score"] = s
        null[i] = ev.monthly_table(work, top_q)[["auc", "prec_k"]].mean().to_numpy()
    return dict(auc_null_mean=null[:, 0].mean(), auc_null_p95=np.percentile(null[:, 0], 95),
                p_perm_auc=(1 + (null[:, 0] >= obs["auc"]).sum()) / (1 + n_perm),
                p_perm_prec=(1 + (null[:, 1] >= obs["prec_k"]).sum()) / (1 + n_perm))


def block(agent, ml, top_q, cost, label, n_boot, n_perm=0):
    keys = agent[["date", "ticker"]].drop_duplicates()
    ml = ml.merge(keys, on=["date", "ticker"])
    ag = agent.merge(ml[["date", "ticker"]].drop_duplicates(), on=["date", "ticker"])
    rows, series = [], {}
    for (model, fset), g in pd.concat([ag, ml]).groupby(["model", "fset"]):
        if len(g["date"].unique()) < 3:
            continue
        r, _ = metrics_for(g, top_q, cost)
        if n_perm and model == agent["model"].iloc[0]:
            r.update(null_test(g, top_q, n_perm))
        rows.append({"block": label, "model": model, "fset": fset, "stock_months": len(g), **r})
        t = ev.monthly_table(g, top_q)
        series[(model, fset)] = t
    res = pd.DataFrame(rows)
    paired = []
    a_key = next((k for k in series if k[0] == agent["model"].iloc[0]), None)
    if a_key is not None:
        for k, t in series.items():
            if k == a_key:
                continue
            for metric in ("auc", "prec_k"):
                d = (series[a_key][metric] - t[metric]).dropna()
                if len(d) >= 3:
                    paired.append({"block": label, "agent_minus": f"{k[0]}/{k[1]}", "metric": metric,
                                   "mean_diff": d.mean(), "n_months": len(d), **ev.mean_diff_bootstrap(d, n_boot)})
    return res, pd.DataFrame(paired)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--agent", required=True, help="agent run folder (predictions.parquet)")
    ap.add_argument("--ml-run", required=True, help="run_experiment.py result folder")
    ap.add_argument("--ml-fset", choices=["full", "firm"], default="firm")
    ap.add_argument("--llm-cutoff", default=None, help="YYYY-MM, end of the LLM's training data")
    ap.add_argument("--top-q", type=float, default=0.2)
    ap.add_argument("--cost", type=float, default=0.002)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--n-perm", type=int, default=500, help="permutation draws for the agent's luck baseline (0 = off)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    agent = pd.read_parquet(Path(a.agent) / "predictions.parquet")
    ml = pd.read_parquet(Path(a.ml_run) / "predictions.parquet")
    ml = ml[ml["fset"] == a.ml_fset]
    for d in (agent, ml):
        d["date"] = pd.to_datetime(d["date"])
    agent = agent.dropna(subset=["score"])
    common = agent[["date", "ticker"]].merge(ml[["date", "ticker"]].drop_duplicates(), on=["date", "ticker"])
    print(f"agent stock-months: {len(agent):,}; also scored by the ML run: {len(common):,} "
          f"({common['date'].nunique()} months, {common['ticker'].nunique()} stocks)")
    if common.empty:
        raise SystemExit("no overlap: run both on the same --raw-dir / market / target / years")

    blocks = [("all", agent)]
    if a.llm_cutoff:
        cut = pd.Timestamp(a.llm_cutoff) + pd.offsets.MonthEnd(0)
        blocks += [(f"<= {a.llm_cutoff} (LLM may remember)", agent[agent["date"] <= cut]),
                   (f"> {a.llm_cutoff} (after cutoff)", agent[agent["date"] > cut])]
    res, paired = [], []
    for label, sub in blocks:
        if sub.empty:
            continue
        r, p = block(sub, ml, a.top_q, a.cost, label, a.n_boot, a.n_perm)
        res.append(r); paired.append(p)
    res = pd.concat(res, ignore_index=True)
    paired = pd.concat(paired, ignore_index=True) if paired else pd.DataFrame()
    show = ["block", "model", "fset", "stock_months", "auc_monthly", "prec_at_k", "base_rate", "Sharpe", "WinRate_vs_bm"]
    print("\n" + res[show].to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    if "p_perm_auc" in res:
        nul = res.dropna(subset=["p_perm_auc"])[["block", "model", "auc_monthly", "auc_null_mean", "auc_null_p95",
                                                  "p_perm_auc", "prec_at_k", "p_perm_prec"]]
        print("\nagent vs. luck (scores shuffled within each month; p = share of shuffles at least as good):")
        print(nul.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    if len(paired):
        print("\nagent minus ML, monthly (positive = agent better):")
        print(paired.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    if a.out:
        out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
        res.to_csv(out / "agent_vs_ml_metrics.csv", index=False)
        paired.to_csv(out / "agent_vs_ml_paired.csv", index=False)
        print(f"\nwritten to {out}")


if __name__ == "__main__":
    main()

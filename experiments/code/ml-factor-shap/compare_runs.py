"""Paired comparison of two experiment runs (e.g. --factor-set base vs extended).

    python compare_runs.py results/base results/ext --labels base extended --out results/base_vs_ext

For every (model, feature set) present in both runs, month by month: AUC, Precision@K and the
net-of-cost portfolio return. Tests H0: B is not better than A (one-sided), reporting
  - paired t-test and Wilcoxon on the monthly differences,
  - circular block bootstrap CI / p-value for the mean difference (robust to autocorrelation),
  - paired block bootstrap of the Sharpe difference.
Both runs must use the same data and target settings; mismatched rows or labels abort.
"""
import argparse
from pathlib import Path

import pandas as pd

import evaluation as ev


def load(run):
    p = pd.read_parquet(Path(run) / "predictions.parquet")
    p["date"] = pd.to_datetime(p["date"])
    return p


def check_same_task(a, b):
    k = ["date", "ticker"]
    ma = a.drop_duplicates(k).set_index(k)["y"]
    mb = b.drop_duplicates(k).set_index(k)["y"]
    if not ma.index.equals(mb.index):
        raise SystemExit(f"runs cover different stock-months ({len(ma)} vs {len(mb)}); "
                         "rerun both with the same data, min-coverage/min-mcap and test years")
    if (ma != mb).any():
        raise SystemExit("labels differ between runs; use the same --target-margin/--target-quantile")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_a"); ap.add_argument("run_b")
    ap.add_argument("--labels", nargs=2, default=["A", "B"])
    ap.add_argument("--top-q", type=float, default=0.2)
    ap.add_argument("--cost", type=float, default=0.002)
    ap.add_argument("--n-boot", type=int, default=5000)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    la, lb = args.labels

    pa, pb = load(args.run_a), load(args.run_b)
    check_same_task(pa, pb)
    keys = sorted(set(map(tuple, pa[["model", "fset"]].drop_duplicates().values))
                  & set(map(tuple, pb[["model", "fset"]].drop_duplicates().values)))
    rows = []
    for model, fset in keys:
        ga = pa[(pa.model == model) & (pa.fset == fset)]
        gb = pb[(pb.model == model) & (pb.fset == fset)]
        ta, tb = ev.monthly_table(ga, args.top_q), ev.monthly_table(gb, args.top_q)
        series = {"auc": (ta["auc"], tb["auc"]), "prec_k": (ta["prec_k"], tb["prec_k"])}
        for metric, (a, b) in series.items():
            d = (b - a).dropna()
            r = ev.paired_tests(b, a)                    # one-sided: B > A
            r.update(ev.mean_diff_bootstrap(d, args.n_boot))
            rows.append(dict(model=model, fset=fset, metric=metric, **{f"mean_{la}": a.mean(), f"mean_{lb}": b.mean()}, **r))
        na = ev.backtest(ga, args.top_q, args.cost)["net"]
        nb = ev.backtest(gb, args.top_q, args.cost)["net"]
        s = ev.sharpe_diff_bootstrap(nb, na, args.n_boot)
        rows.append(dict(model=model, fset=fset, metric="sharpe_net", **{f"mean_{la}": s["sharpe_b"], f"mean_{lb}": s["sharpe_a"]},
                         mean_diff=s["diff"], boot_ci_lo=s["ci_lo"], boot_ci_hi=s["ci_hi"],
                         p_boot=s["p_one_sided"], n_months=s["n_months"]))
    res = pd.DataFrame(rows)       # for sharpe_net the mean_* columns hold each run's Sharpe
    print(f"difference = {lb} - {la}; one-sided H0: {lb} not better than {la}")
    print(res.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    if args.out:
        out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
        res.to_csv(out / "paired_comparison.csv", index=False)


if __name__ == "__main__":
    main()

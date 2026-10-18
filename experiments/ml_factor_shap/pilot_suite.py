"""Small-sample pilot: the runs worth doing when the period and the universe cannot grow.

    python pilot_suite.py --raw-dir data/real --out-root results/pilot            # real data, --quick profile
    python pilot_suite.py --data synthetic --out-root results/pilot_synth --trials 3

Steps (each prints where its output went):
  0. factor_ic.py                      do any of the factors carry signal at all?
  A. regularised search, raw macro     --small-data --macro-mode raw
  B. regularised search, macro regimes --small-data --macro-mode regime     (A vs B isolates the macro encoding)
  C. as B with --target-quantile 0.8   top-20 % by monthly excess return    (label comparison; not paired with A/B
                                       because the labels differ)
  compare_runs.py A B                  paired monthly tests, Holm-aware reading is up to you
Everything after `--` is passed to every run_experiment.py call, e.g.  -- --factor-set extended
"""
import argparse
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent


def run(args):
    print("\n$", " ".join(args), flush=True)
    subprocess.run([sys.executable, *args], check=True, cwd=HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", choices=["synthetic", "real"], default="real")
    ap.add_argument("--raw-dir", default="data/real")
    ap.add_argument("--out-root", default="results/pilot")
    ap.add_argument("--trials", type=int, default=None, help="override Optuna trials")
    ap.add_argument("extra", nargs="*", help="passed to run_experiment.py (put after --)")
    a = ap.parse_args()
    root = Path(a.out_root)
    common = ["run_experiment.py", "--quick", "--small-data", "--data", a.data, "--raw-dir", a.raw_dir, *a.extra]
    if a.trials:
        common += ["--trials", str(a.trials)]

    ic_args = ["factor_ic.py", "--data", a.data, "--raw-dir", a.raw_dir, "--out", str(root / "factor_ic")]
    if a.data == "real":
        ic_args += ["--market", "KOSPI", "--top-n-mcap", "100", "--start-date", "2020-01-02"]
    run(ic_args)

    runs = {"A_raw": ["--macro-mode", "raw"], "B_regime": ["--macro-mode", "regime"],
            "C_regime_q80": ["--macro-mode", "regime", "--target-quantile", "0.8"]}
    for name, extra in runs.items():
        run([*common, *extra, "--out", str(root / name)])
    run(["compare_runs.py", str(root / "A_raw"), str(root / "B_regime"), "--labels", "raw", "regime",
         "--out", str(root / "A_vs_B")])

    rows = []
    for name in runs:
        m = pd.read_csv(root / name / "metrics.csv")
        m = m[m["fset"].isin(["full", "firm"])].assign(run=name)
        rows.append(m[["run", "model", "fset", "auc_monthly", "prec_at_k", "base_rate", "Sharpe", "WinRate_vs_bm"]])
    summary = pd.concat(rows)
    summary.to_csv(root / "summary.csv", index=False)
    print("\n== summary (monthly AUC, Precision@K, Sharpe) ==")
    print(summary.to_string(index=False, float_format=lambda x: f"{x:.3f}"))


if __name__ == "__main__":
    main()

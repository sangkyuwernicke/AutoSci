"""make_summary_table generalisation: models read from the data, count-style top-q, benchmark rows, wording.
Run: python tests/test_summary_table.py"""
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import evaluation as ev
from make_summary_table import describe, models_in, panel_a, pooled_effects

MONTHS = pd.date_range("2022-01-31", periods=14, freq="ME")
N_STOCKS, TOP_Q = 40, 10


def make_run(seed: int, models=("lgbm", "logit")) -> pd.DataFrame:
    rng = np.random.default_rng(0)                       # same stocks, labels and returns in both runs
    base = [dict(date=d, ticker=f"{i:06d}", y=int(rng.random() > 0.5), ret_next=rng.normal(0, 0.05),
                 mkt_next=0.01, mcap=float(N_STOCKS - i), test_year=d.year) for d in MONTHS for i in range(N_STOCKS)]
    base = pd.DataFrame(base)
    srng = np.random.default_rng(seed)                   # scores differ between the runs
    parts = [base.assign(model=m, fset=f, score=srng.random(len(base))) for m in models for f in ("firm", "full")]
    return pd.concat(parts, ignore_index=True)


def write_indices(d: Path):
    r = np.random.default_rng(5).normal(0.008, 0.04, len(MONTHS))
    for name, scale in (("kospi200_ew_official_monthly.csv", 1.0), ("kospi200_official_monthly.csv", 1.5)):
        pd.Series(r * scale, index=MONTHS, name="x").to_csv(d / name)
    return r


def test_models_come_from_the_data():
    runs = {"none": make_run(1), "finbert": make_run(2)}
    assert models_in(runs) == ["logit", "lgbm"], "preferred order (logit before lgbm), only models present in both runs"
    runs["finbert"] = runs["finbert"][runs["finbert"].model == "logit"]
    assert models_in(runs) == ["logit"], "a model missing from one run is dropped"


def test_panel_a_with_a_count_book_and_benchmarks():
    runs = {"none": make_run(1), "finbert": make_run(2)}
    with tempfile.TemporaryDirectory() as t:
        ref = Path(t)
        r = write_indices(ref)
        tab, cells = panel_a(runs, TOP_Q, 0.002, ref_dir=ref, models=models_in(runs))
        eff = pooled_effects(cells, n_boot=200, models=models_in(runs))
    assert list(tab.index) == ["logit", "lgbm", "Model mean", "EW of test universe (no model, no cost)",
                               "KOSPI200 EW official (primary benchmark)", "KOSPI200 cap-weighted official"]
    assert np.isclose(tab.loc["Model mean", "AUC Firm"], tab.loc[["logit", "lgbm"], "AUC Firm"].mean())
    sh = float(ev.perf_stats(pd.Series(r))["Sharpe"])
    assert np.isclose(tab.loc["KOSPI200 EW official (primary benchmark)", "Sharpe Firm"], sh)
    assert tab.loc["KOSPI200 EW official (primary benchmark)", "Sharpe Firm"] == tab.loc["KOSPI200 EW official (primary benchmark)", "Sharpe Firm+Macro+Sent"]
    assert list(eff.index) == ["Macro effect (Firm+Macro - Firm)", "Sentiment effect (+FinBert - none)"]
    assert int(eff["n_months"].iloc[0]) >= 10


def test_wording_matches_the_setup():
    runs = {"none": make_run(1), "finbert": make_run(2)}
    text = describe(runs, TOP_Q, 0.002)
    assert "top 10 stocks" in text and "top 10%" not in text and "1000%" not in text, text
    assert "14 test months" in text
    frac = describe(runs, 0.2, 0.002)
    assert "top 20%" in frac


for t in (test_models_come_from_the_data, test_panel_a_with_a_count_book_and_benchmarks, test_wording_matches_the_setup):
    t()
print("summary-table tests passed")

"""Pilot tooling: factor IC, small-data search space, macro regimes, price-only panel. Run: python tests/test_pilot.py"""
import sys, tempfile
from pathlib import Path

import numpy as np
import optuna
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MACRO
from data_real import build_panel
from factor_ic import monthly_rank_ic, newey_west_t, summarize
from features import macro_to_regime
from models import suggest

rng = np.random.default_rng(0)

# ---- factor IC: a planted signal is found, noise is not, value ratios are read as "cheap is good"
dates = pd.date_range("2020-01-31", periods=48, freq="ME")
rows = []
for d in dates:
    n = 120
    a, b = rng.normal(size=n), rng.normal(size=n)
    per = np.exp(rng.normal(2.5, 0.5, n))
    excess = 0.4 * a + 0.4 * (1 / per - (1 / per).mean()) / (1 / per).std() + rng.normal(size=n)
    rows.append(pd.DataFrame(dict(date=d, ticker=[f"{i:06d}" for i in range(n)], A=a, B=b, PER=per,
                                  ret_next=excess * 0.05, mkt_next=0.0)))
panel = pd.concat(rows)
ic = monthly_rank_ic(panel, ["A", "B", "PER"])
res = summarize(ic)
assert res.loc["A", "mean_ic"] > 0.2 and abs(res.loc["A", "t_nw"]) > 4
assert abs(res.loc["B", "mean_ic"]) < 0.1
assert res.loc["PER", "mean_ic"] > 0.15, "PER is inverted: low PER (cheap) with higher return must give a positive IC"
assert np.isfinite(newey_west_t(ic["A"]))
assert res.index[0] in ("A", "PER"), "summary is sorted by |t|"

# ---- small-data search space stays inside its bounds
def check(name, check_fn, n=25):
    seen = []

    def obj(t):
        p = suggest(name, t, small=True)
        seen.append(p)
        return 0.0
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    optuna.create_study().optimize(obj, n_trials=n)
    assert all(check_fn(p) for p in seen), name

check("xgb", lambda p: p["max_depth"] <= 4 and p["n_estimators"] <= 300 and p["learning_rate"] <= 0.08)
check("lgbm", lambda p: p["max_depth"] <= 4 and p["min_child_samples"] >= 100)
check("catboost", lambda p: p["max_depth"] <= 4 and p["l2_leaf_reg"] >= 3)
check("dtree", lambda p: p["max_depth"] <= 4 and p["min_samples_leaf"] >= 100)
check("logit", lambda p: p["C"] <= 1)

# ---- macro regimes: coarse, causal
d = pd.date_range("2020-01-31", periods=8, freq="ME")
vals = [1, 2, 3, 2, 2, 5, 1, 4]
p = pd.DataFrame({"date": np.repeat(d, 3), "ticker": list("abc") * 8})
for c in MACRO:
    p[c] = np.repeat(vals, 3).astype(float)
r = macro_to_regime(p, MACRO)
assert r.groupby("date")["BASE_RATE"].first().tolist() == [0.5, 1, 1, 0.5, 0.5, 1, 0, 1]
assert set(r["VKOSPI"].unique()) <= {0.0, 0.5, 1.0} and (r["VKOSPI_RAW"] == p["VKOSPI"]).all()
p2 = p.copy(); p2.loc[p2["date"] > d[4], MACRO] = 100.0            # rewrite the future ...
r2 = macro_to_regime(p2, MACRO)
assert r2.groupby("date")["BASE_RATE"].first().tolist()[:5] == [0.5, 1, 1, 0.5, 0.5], "must not look ahead"

# ---- price-only panel needs neither fundamentals nor macro
with tempfile.TemporaryDirectory() as tmp:
    raw = Path(tmp)
    months = pd.date_range("2020-01-31", "2022-12-31", freq="ME")
    recs = []
    for t in ["000010", "000020", "000030"]:
        px = 100 * np.cumprod(1 + rng.normal(0, 0.05, len(months)))
        for k, m in enumerate(months):
            recs.append(dict(date=m, ticker=t, name=t, market="KOSPI", close=px[k], shares=1e6, mcap=px[k] * 1e6,
                             ret1=np.nan if k == 0 else px[k] / px[k - 1] - 1, adj_close=px[k], seg=1, eligible=True))
    pd.DataFrame(recs).to_parquet(raw / "prices_monthly.parquet")
    days = pd.bdate_range("2020-01-01", "2023-01-31")
    pd.DataFrame(dict(date=days, market="KOSPI", close=2000 * np.exp(np.cumsum(rng.normal(0, 0.008, len(days)))))
                 ).to_parquet(raw / "index.parquet")
    po = build_panel(raw, market="KOSPI", price_only=True)
    assert {"SIZE", "RET_1M", "RET_12M", "ret_next", "mkt_next"} <= set(po.columns)
    assert not (set(MACRO) & set(po.columns)) and len(po) > 0
print("pilot tooling tests passed")

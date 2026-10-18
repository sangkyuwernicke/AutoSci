"""Prediction metrics, long-only top-quantile backtest, and hypothesis tests (H1, H2)."""
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import average_precision_score, roc_auc_score


# ----------------------------------------------------------------- prediction metrics
def monthly_table(pred, top_q=0.2):
    """Per-month AUC and Precision@top_q for one (model, feature set) prediction frame."""
    rows = {}
    for d, g in pred.groupby("date"):
        k = max(1, int(np.ceil(top_q * len(g))))
        top = g.nlargest(k, "score")
        auc = roc_auc_score(g["y"], g["score"]) if g["y"].nunique() == 2 else np.nan
        rows[d] = dict(auc=auc, prec_k=top["y"].mean(), base_rate=g["y"].mean())
    return pd.DataFrame(rows).T.sort_index()


def prediction_metrics(pred, top_q=0.2):
    m = monthly_table(pred, top_q)
    return dict(
        auc_pooled=roc_auc_score(pred["y"], pred["score"]),
        pr_auc=average_precision_score(pred["y"], pred["score"]),
        auc_monthly=m["auc"].mean(), prec_at_k=m["prec_k"].mean(), base_rate=m["base_rate"].mean())


# ------------------------------------------------------------------------- backtest
def backtest(pred, top_q=0.2, cost=0.002):
    """Equal-weight top-`top_q` portfolio formed at each month-end t, held over month t+1.
    Cost = `cost` x sum|dw| (so a full one-sided rebalance of the book costs 2*cost)."""
    prev = pd.Series(dtype=float)
    out = []
    for d, g in pred.groupby("date"):
        top = g.nlargest(max(1, int(np.ceil(top_q * len(g)))), "score")
        w = pd.Series(1.0 / len(top), index=top["ticker"].values)
        dw = w.sub(prev, fill_value=0.0).abs().sum() if len(prev) else 1.0
        out.append(dict(date=d, gross=top["ret_next"].mean(), bench=g["mkt_next"].iloc[0],
                        universe=g["ret_next"].mean(), turnover=0.5 * dw, cost=cost * dw,
                        first=len(prev) == 0))
        prev = w
    r = pd.DataFrame(out).set_index("date")
    r["net"] = r["gross"] - r["cost"]
    return r


def perf_stats(ret, bench=None, turnover=None):
    ret = pd.Series(ret).dropna()
    wealth = (1 + ret).cumprod()
    s = dict(CAGR=wealth.iloc[-1] ** (12 / len(ret)) - 1,
             Sharpe=ret.mean() / ret.std(ddof=1) * np.sqrt(12),
             MDD=(wealth / wealth.cummax() - 1).min(), WinRate_abs=(ret > 0).mean())
    if bench is not None:
        s["WinRate_vs_bm"] = (ret > bench.loc[ret.index]).mean()
    if turnover is not None:
        s["Turnover"] = turnover.mean()
    return s


# ------------------------------------------------------------------ hypothesis tests
def paired_tests(a, b):
    """H1 tests on aligned monthly series, a (integrated) vs b (firm-only). One-sided a > b."""
    d = (a - b).dropna()
    t = stats.ttest_1samp(d, 0.0, alternative="greater")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            w = stats.wilcoxon(d, alternative="greater").pvalue
    except ValueError:
        w = np.nan
    return dict(mean_diff=d.mean(), t_stat=t.statistic, p_ttest=t.pvalue, p_wilcoxon=w, n_months=len(d))


def sharpe_diff_bootstrap(a, b, n_boot=5000, block=3, seed=0):
    """Paired circular block bootstrap of Sharpe(a) - Sharpe(b); one-sided p for H0: diff <= 0."""
    x = pd.concat([a, b], axis=1).dropna().to_numpy()
    n = len(x)
    rng = np.random.default_rng(seed)

    def sharpe(r):
        return r.mean(0) / r.std(0, ddof=1) * np.sqrt(12)

    obs = sharpe(x)
    obs_diff = obs[0] - obs[1]
    n_blocks = int(np.ceil(n / block))
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        starts = rng.integers(0, n, n_blocks)
        idx = ((starts[:, None] + np.arange(block)) % n).reshape(-1)[:n]
        s = sharpe(x[idx])
        diffs[i] = s[0] - s[1]
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return dict(sharpe_a=obs[0], sharpe_b=obs[1], diff=obs_diff, ci_lo=lo, ci_hi=hi,
                p_one_sided=(diffs <= 0).mean(), n_months=n)


def mean_diff_bootstrap(d, n_boot=5000, block=3, seed=0):
    """Circular block bootstrap CI and one-sided p (H0: mean <= 0) for the mean of a monthly difference series."""
    x = pd.Series(d).dropna().to_numpy()
    n = len(x)
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(n / block))
    means = np.empty(n_boot)
    for i in range(n_boot):
        starts = rng.integers(0, n, n_blocks)
        idx = ((starts[:, None] + np.arange(block)) % n).reshape(-1)[:n]
        means[i] = x[idx].mean()
    lo, hi = np.percentile(means, [2.5, 97.5])
    return dict(boot_ci_lo=lo, boot_ci_hi=hi, p_boot=(means <= 0).mean())

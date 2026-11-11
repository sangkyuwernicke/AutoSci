"""Prediction metrics, long-only top-quantile backtest, and hypothesis tests (H1, H2)."""
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import average_precision_score, roc_auc_score


def rank_desc(g, seed=0):
    """Rows of one month ordered by score, best first. Ties are broken by a seeded shuffle, so an (almost) constant score
    does not silently pick the stocks that happen to come first in the frame (e.g. the lowest tickers)."""
    return g.sample(frac=1.0, random_state=seed).sort_values("score", ascending=False, kind="mergesort")


def select_k(n, top):
    """Portfolio size for a month with `n` stocks: `top` < 1 is a fraction (ceil), `top` >= 1 is a fixed count."""
    return max(1, min(n, int(top))) if top >= 1 else max(1, int(np.ceil(top * n)))


# ----------------------------------------------------------------- prediction metrics
def monthly_table(pred, top_q=0.2):
    """Per-month AUC and Precision@K for one (model, feature set) prediction frame. `top_q`: fraction (<1) or count (>=1)."""
    rows = {}
    for d, g in pred.groupby("date"):
        k = select_k(len(g), top_q)
        top = rank_desc(g).iloc[:k]
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
def _weights(top, rest_max, weighting):
    """Weights of the held stocks. equal: 1/k. prob: proportional to the predicted P(up). excess: proportional to the
    score above the best excluded stock's score (a sharper tilt; falls back to equal if all excess are zero)."""
    s = top["score"].to_numpy(float)
    if weighting == "prob":
        raw = s
    elif weighting == "excess":
        raw = s - (rest_max if np.isfinite(rest_max) else s.min())
    else:
        raw = np.ones_like(s)
    raw = np.clip(raw, 0.0, None)
    return pd.Series(raw / raw.sum() if raw.sum() > 0 else np.full(len(s), 1.0 / len(s)), index=top["ticker"].values)


def backtest(pred, top_q=0.2, cost=0.002, weighting="equal"):
    """Top-`top_q` (fraction if < 1, else number of stocks) portfolio formed at each month-end t, held over month t+1.
    `weighting`: equal (default), prob or excess (see _weights).
    Cost = `cost` x sum|dw| (so a full one-sided rebalance of the book costs 2*cost)."""
    prev = pd.Series(dtype=float)
    out = []
    for d, g in pred.groupby("date"):
        g = rank_desc(g)
        k = select_k(len(g), top_q)
        top, rest = g.iloc[:k], g.iloc[k:]
        w = _weights(top, rest["score"].max() if len(rest) else np.nan, weighting)
        dw = w.sub(prev, fill_value=0.0).abs().sum() if len(prev) else 1.0
        out.append(dict(date=d, gross=float((top["ret_next"].to_numpy() * w.to_numpy()).sum()), bench=g["mkt_next"].iloc[0],
                        universe=g["ret_next"].mean(), turnover=0.5 * dw, cost=cost * dw,
                        first=len(prev) == 0))
        prev = w
    r = pd.DataFrame(out).set_index("date")
    r["net"] = r["gross"] - r["cost"]
    return r


def cap_weighted_top(pred, n=200):
    """KOSPI200 proxy: each month-end the `n` largest stocks by market cap in the universe, cap-weighted, held one month.
    Not the official index (no official constituent list; financials / SPACs are already excluded from the universe)."""
    out = {}
    for d, g in pred.drop_duplicates(["date", "ticker"]).groupby("date"):
        top = g.nlargest(n, "mcap")
        out[d] = float((top["ret_next"] * top["mcap"]).sum() / top["mcap"].sum())
    return pd.Series(out).sort_index()


def index_monthly_return(csv_path, dates):
    """Next-month price return of an index from a KRX download (`일자`, `종가`), aligned to the model's decision dates:
    close at the last trading day <= d+1 month-end over close at the last trading day <= d."""
    d = pd.read_csv(csv_path, encoding="utf-8-sig")
    s = pd.Series(d["종가"].astype(float).to_numpy(), index=pd.to_datetime(d["일자"])).sort_index()
    dates = pd.DatetimeIndex(dates)
    now = s.asof(dates).to_numpy()
    nxt = s.asof(dates + pd.offsets.MonthEnd(1)).to_numpy()
    return pd.Series(nxt / now - 1.0, index=dates)


def perf_stats(ret, bench=None, turnover=None):
    ret = pd.Series(ret).dropna()
    wealth = (1 + ret).cumprod()
    s = dict(CAGR=wealth.iloc[-1] ** (12 / len(ret)) - 1,
             Sharpe=ret.mean() / ret.std(ddof=1) * np.sqrt(12),
             MDD=(wealth / wealth.cummax() - 1).min(), WinRate_abs=(ret > 0).mean())
    if bench is not None:
        b = bench.loc[ret.index]
        ex = ret - b
        s["WinRate_vs_bm"] = (ret > b).mean()
        s["Excess_mo"] = ex.mean()                                    # mean monthly excess return over the benchmark
        s["t_excess"] = ex.mean() / ex.std(ddof=1) * np.sqrt(len(ex)) if len(ex) > 1 and ex.std(ddof=1) > 0 else np.nan
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


def holm_adjust(p):
    """Holm step-down adjusted p-values (family-wise error control); NaN stays NaN."""
    p = pd.Series(p, dtype=float)
    ok = p.notna()
    order = p[ok].sort_values().index
    m = len(order)
    adj, run = {}, 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * p[i]))
        adj[i] = run
    return p.index.map(lambda i: adj.get(i, np.nan)).to_numpy()

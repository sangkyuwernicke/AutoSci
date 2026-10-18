"""SHAP global / regime / interaction analysis (H3)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
import warnings
from scipy.stats import spearmanr

warnings.filterwarnings("ignore", message=".*TreeExplainer shap values output has changed.*")
from config import MACRO


def fold_shap(model, X, n_inter=2000, seed=0):
    """SHAP values (log-odds) for all rows of X, interaction values for a random subsample."""
    ex = shap.TreeExplainer(model)
    sv = ex.shap_values(X)
    sv = sv[1] if isinstance(sv, list) else sv
    sv = np.asarray(sv)
    if sv.ndim == 3:
        sv = sv[..., 1]
    idx = np.random.default_rng(seed).choice(len(X), min(n_inter, len(X)), replace=False)
    iv = np.asarray(ex.shap_interaction_values(X.iloc[idx]))
    if iv.ndim == 4:
        iv = iv[..., 1]
    return pd.DataFrame(sv, columns=X.columns, index=X.index), idx, iv


def interaction_matrix(iv, all_features, firm_factors):
    """Mean |interaction| (both triangles summed), macro rows x firm columns."""
    m = np.abs(iv).mean(0) * 2
    ix = {f: i for i, f in enumerate(all_features)}
    return pd.DataFrame([[m[ix[a], ix[b]] for b in firm_factors] for a in MACRO],
                        index=MACRO, columns=firm_factors)


def regime_flags(monthly, min_months=6):
    """High/low regime flag per month from a monthly macro series. Policy rates sit at one value for long
    stretches, so `> median` can leave the high group empty; fall back to `>= median`, then fail loudly."""
    med = monthly.median()
    for flag in (monthly > med, monthly >= med):
        if flag.sum() >= min_months and (~flag).sum() >= min_months:
            return flag
    raise ValueError(f"cannot split {monthly.name} into two regimes with >= {min_months} months each "
                     f"(median {med}, {monthly.nunique()} distinct values)")


def regime_analysis(sv, Xf, dates, high, n_perm=2000, seed=0):
    """Compare factor importance/direction between high and low regimes of one macro variable.

    sv, Xf : SHAP values and feature values (firm factors only), aligned rows.
    dates  : Series of feature dates per row.   high : bool Series per row (macro > median over test months).
    The permutation test shuffles the regime label across *months* (the regime is constant within
    a month), testing whether the importance ranking differs more than months drawn at random.
    """
    absmonth = sv.abs().groupby(dates.values).mean()
    flag = high.groupby(dates.values).first().loc[absmonth.index].to_numpy()
    imp_h, imp_l = absmonth[flag].mean(), absmonth[~flag].mean()

    def dissim(h):
        return 1 - spearmanr(absmonth[h].mean(), absmonth[~h].mean())[0]

    obs = dissim(flag)
    rng = np.random.default_rng(seed)
    perm = np.array([dissim(rng.permutation(flag)) for _ in range(n_perm)])
    p = (1 + (perm >= obs).sum()) / (1 + n_perm)

    def direction(mask):
        return pd.Series({f: spearmanr(Xf.loc[mask, f], sv.loc[mask, f])[0] for f in sv.columns})

    dir_h, dir_l = direction(high.to_numpy()), direction(~high.to_numpy())
    tab = pd.DataFrame({"imp_high": imp_h, "imp_low": imp_l,
                        "rank_high": imp_h.rank(ascending=False).astype(int),
                        "rank_low": imp_l.rank(ascending=False).astype(int),
                        "dir_high": dir_h, "dir_low": dir_l})
    tab["sign_flip"] = np.sign(tab.dir_high) != np.sign(tab.dir_low)
    summary = dict(spearman_rank_corr=1 - obs, dissimilarity=obs, p_perm=p,
                   n_months_high=int(flag.sum()), n_months_low=int((~flag).sum()))
    return tab, summary


# --------------------------------------------------------------------------- plots
def plot_summary(sv, X, path, max_rows=5000):
    idx = np.random.default_rng(0).choice(len(X), min(max_rows, len(X)), replace=False)
    shap.summary_plot(sv.to_numpy()[idx], X.iloc[idx], show=False, max_display=min(25, X.shape[1]))
    plt.tight_layout(); plt.savefig(path, dpi=150); plt.close()


def plot_regime_bars(tab, var, path):
    t = tab.sort_values("imp_high")
    y = np.arange(len(t))
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.barh(y - 0.2, t.imp_low, 0.4, label=f"low {var}")
    ax.barh(y + 0.2, t.imp_high, 0.4, label=f"high {var}")
    ax.set_yticks(y, t.index); ax.set_xlabel("mean |SHAP|"); ax.legend()
    ax.set_title(f"Firm-factor importance by {var} regime")
    plt.tight_layout(); plt.savefig(path, dpi=150); plt.close()


def plot_interaction_heatmap(mat, path):
    fig, ax = plt.subplots(figsize=(10, 3.5))
    im = ax.imshow(mat.to_numpy(), aspect="auto", cmap="viridis")
    ax.set_xticks(range(mat.shape[1]), mat.columns, rotation=60, ha="right")
    ax.set_yticks(range(mat.shape[0]), mat.index)
    fig.colorbar(im, label="mean |SHAP interaction|"); ax.set_title("Macro x firm-factor interaction")
    plt.tight_layout(); plt.savefig(path, dpi=150); plt.close()


def plot_pair_scatter(iv, Xsub, firm, macro, path):
    ix = {f: i for i, f in enumerate(Xsub.columns)}
    val = 2 * iv[:, ix[firm], ix[macro]]
    fig, ax = plt.subplots(figsize=(6, 4.5))
    sc = ax.scatter(Xsub[firm], val, c=Xsub[macro], s=6, cmap="coolwarm")
    fig.colorbar(sc, label=macro); ax.set_xlabel(f"{firm} (cross-sectional score)")
    ax.set_ylabel(f"SHAP interaction {firm} x {macro}")
    plt.tight_layout(); plt.savefig(path, dpi=150); plt.close()

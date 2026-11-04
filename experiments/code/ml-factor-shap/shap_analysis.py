"""SHAP global / regime / interaction analysis (H3).

Also provides gating-weight analysis for the RegimeGatedScorer
(--macro-role gating), which is the structural alternative to SHAP
interaction values: instead of post-hoc attribution, the model exposes
w(m_t) = Σ_k α_k(m_t) β_k directly for every test month.
"""
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


# ══════════════════════════════════════════════════════════════════ SHAP plots
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


# ═══════════════════════════════════ Macro-Gated model interpretability
def fold_gating_weights(model, X, macro_cols, dates):
    """Factor weight time series from a RegimeGatedScorer over one test fold.

    For each unique month in `dates`, queries model.factor_weights(m_t)
    to obtain w(m_t) = Σ_k α_k(m_t) β_k — the net loading on each firm
    factor at the prevailing macro state.

    Parameters
    ──────────
    model      : fitted RegimeGatedScorer
    X          : DataFrame with both firm_cols and macro_cols present
    macro_cols : list of macro column names
    dates      : Series of feature dates aligned with X rows

    Returns
    ───────
    pd.DataFrame  shape (T_months, F_factors), indexed by date.
    """
    monthly = X.assign(_date=dates.values).groupby("_date")[macro_cols].first()
    weights = {d: model.factor_weights(row.values) for d, row in monthly.iterrows()}
    return pd.DataFrame(weights).T.sort_index()


def plot_gating_weights(weight_series, monthly_macro, path):
    """Line chart of effective factor weights w(m_t) over time.

    Upper panel: each firm factor's effective weight (may be negative = flipped).
    Lower panel: BASE_RATE level for macro context (if present).

    Parameters
    ──────────
    weight_series : DataFrame (T_months, F_factors) from fold_gating_weights
    monthly_macro : DataFrame of raw macro values indexed by date
    path          : output file path
    """
    has_rate = "BASE_RATE" in monthly_macro.columns
    n_panels = 2 if has_rate else 1
    ratios = [3, 1] if has_rate else [1]
    fig, axes = plt.subplots(n_panels, 1, figsize=(12, 4 + 2 * n_panels),
                             sharex=True, gridspec_kw={"height_ratios": ratios})
    ax = axes[0] if has_rate else axes

    for col in weight_series.columns:
        ax.plot(weight_series.index, weight_series[col], label=col, linewidth=0.9)
    ax.axhline(0, color="black", linewidth=0.6, linestyle="--", alpha=0.6)
    ax.set_ylabel("Effective factor weight  w(m_t)")
    ax.set_title("Macro-gated factor weights over time  [w(m) = Σ_k α_k(m)·β_k]")
    ax.legend(fontsize=7, ncol=min(5, len(weight_series.columns)), loc="upper left")

    if has_rate:
        common = monthly_macro.index.intersection(weight_series.index)
        axes[1].plot(common, monthly_macro.loc[common, "BASE_RATE"],
                     color="tab:red", linewidth=0.9)
        axes[1].set_ylabel("BASE_RATE")
        axes[1].set_xlabel("Date")

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_regime_centroids(model, path):
    """Bar chart of K regime centroids in macro space.

    Values are min-max normalised per variable so all axes share [0, 1].
    Each bar group represents one macro variable; bars within the group
    are the K regimes.
    """
    df = model.regime_centroids_df()
    df_norm = (df - df.min()) / (df.max() - df.min() + 1e-9)
    ax = df_norm.T.plot(kind="bar", figsize=(8, 4))
    ax.set_title("Regime centroids (min-max normalised per macro variable)")
    ax.set_ylabel("Normalised value")
    ax.set_xlabel("Macro variable")
    ax.legend(title="Regime", bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

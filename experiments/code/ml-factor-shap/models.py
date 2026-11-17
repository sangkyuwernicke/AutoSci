"""Model zoo + Optuna search spaces. Every model exposes a scalar score via `score()`.

Two model families:
  - Standard sklearn-compatible classifiers (logit, ridge, dtree, rf, xgb, lgbm, catboost)
  - RegimeGatedScorer  : macro-conditioned factor weighter. Macro variables only control
    *which factor-weight vector* is applied; they never enter directly as predictors.
    Use with --macro-role gating in run_experiment.py.
"""
import warnings

import numpy as np
import pandas as pd
import optuna
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

optuna.logging.set_verbosity(optuna.logging.WARNING)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*penalty.*")


# ══════════════════════════════════════════════════════════ Macro-Gated Model
class RegimeGatedScorer:
    """Macro-Conditioned Factor Weighter (Regime-Gated Mixture of Experts).

    Architecture
    ────────────
      macro state m_t  →  soft regime weights α_k(m_t),   k = 1 … K
      firm factors z_i →  expert k predicts  p_k = σ(β_k ᵀ z_i + b_k)
      final score      =  Σ_k  α_k(m_t) · p_k(z_i)

    Macro variables only enter via the gating network that decides which
    factor-weight vector to apply; they are NEVER direct predictors of a
    stock's return for a given factor value.  This makes the macro role
    explicit and interpretable via `factor_weights(m)`.

    Parameters
    ──────────
    firm_cols  : list of firm-factor column names (inputs to each expert)
    macro_cols : list of macro column names (inputs to the gating network)
    n_regimes  : K — number of regime clusters (Optuna-tunable)
    C          : L2 regularisation strength for each expert logistic
    temperature: softness of regime assignment; small → hard assignment
    seed       : random seed for KMeans
    """

    def __init__(self, firm_cols, macro_cols, n_regimes=4, C=1.0,
                 temperature=0.5, seed=0):
        self.firm_cols = list(firm_cols)
        self.macro_cols = list(macro_cols)
        self.n_regimes = n_regimes
        self.C = C
        self.temperature = temperature
        self.seed = seed

    # ---------------------------------------------------------------- helpers
    def _prep_macro(self, X, fit=False):
        """Standardise macro columns; NaN → 0 after scaling."""
        M = np.nan_to_num(np.asarray(X[self.macro_cols], dtype=float), nan=0.0)
        if fit:
            self._m_mean = M.mean(0)
            self._m_std = M.std(0) + 1e-9
        return (M - self._m_mean) / self._m_std

    def _prep_firm(self, X, fit=False):
        """Standardise firm-factor columns; NaN → 0 after scaling."""
        Z = np.nan_to_num(np.asarray(X[self.firm_cols], dtype=float), nan=0.0)
        if fit:
            self._z_mean = Z.mean(0)
            self._z_std = Z.std(0) + 1e-9
        return (Z - self._z_mean) / self._z_std

    def _soft_weights(self, M_scaled):
        """Softmax(−‖m − centroid_k‖ / temperature): shape (N, K)."""
        diff = M_scaled[:, None, :] - self.centroids_[None, :, :]   # (N, K, D)
        dists = np.linalg.norm(diff, axis=2)                         # (N, K)
        logits = -dists / (self.temperature + 1e-9)
        logits -= logits.max(axis=1, keepdims=True)
        w = np.exp(logits)
        return w / w.sum(axis=1, keepdims=True)

    # ------------------------------------------------------------ sklearn API
    def fit(self, X, y):
        """Fit gating centroids and K expert logistic regressors.

        X must be a DataFrame with both firm_cols and macro_cols present.
        """
        M = self._prep_macro(X, fit=True)
        Z = self._prep_firm(X, fit=True)
        y = np.asarray(y)

        # Cluster on deduplicated monthly macro states (macro is constant
        # within a month, so deduplication avoids per-stock redundancy).
        _, first = np.unique(np.round(M, 8), axis=0, return_index=True)
        K = min(self.n_regimes, len(first))
        km = KMeans(n_clusters=K, random_state=self.seed, n_init=10)
        km.fit(M[first])
        self.centroids_ = km.cluster_centers_   # (K, D_macro)

        # Soft regime assignment for all training rows
        alpha = self._soft_weights(M)            # (N, K)

        # One logistic per regime, weighted by soft assignment α_k
        self.experts_ = []
        for k in range(K):
            lr = LogisticRegression(C=self.C, solver="liblinear", max_iter=500)
            lr.fit(Z, y, sample_weight=alpha[:, k])
            self.experts_.append(lr)
        return self

    def predict_proba(self, X):
        M = self._prep_macro(X)
        Z = self._prep_firm(X)
        alpha = self._soft_weights(M)            # (N, K)
        prob1 = sum(
            alpha[:, k] * e.predict_proba(Z)[:, 1]
            for k, e in enumerate(self.experts_)
        )
        return np.column_stack([1 - prob1, prob1])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)

    # ---------------------------------------------------- interpretability
    def factor_weights(self, m_state):
        """Effective factor weight vector for one macro state.

        Parameters
        ──────────
        m_state : array-like, length len(macro_cols)
            Raw (un-scaled) macro values for a single month.

        Returns
        ───────
        pd.Series  w(m) = Σ_k α_k(m) · β_k,  indexed by firm_cols.

        Positive entry  → factor signal amplified in this macro state.
        Negative entry  → factor signal is flipped (counter-cyclical).
        Near zero       → factor is ignored in this macro environment.
        """
        m = np.nan_to_num(np.asarray(m_state, dtype=float), nan=0.0)
        m_scaled = (m - self._m_mean) / self._m_std
        alpha = self._soft_weights(m_scaled[None, :])[0]        # (K,)
        betas = np.array([e.coef_[0] for e in self.experts_])   # (K, F)
        return pd.Series(alpha @ betas, index=self.firm_cols)

    def regime_centroids_df(self):
        """K regime centroids in original (un-scaled) macro units."""
        return pd.DataFrame(
            self.centroids_ * self._m_std + self._m_mean,
            columns=self.macro_cols,
            index=[f"regime_{k}" for k in range(len(self.centroids_))],
        )


# ══════════════════════════════════════════════════════════ Optuna search spaces
def suggest(name, t, small=False):
    """Search space per model (the plan's tuning list: depth, lr, n_estimators, subsample,
    colsample, reg_alpha, reg_lambda -- applied wherever the algorithm has the knob).

    small=True is for a few thousand training rows: shallow trees, large leaves, few and slow rounds, heavier
    regularisation. With tiny samples the big space mostly lets the tuner pick whatever fits validation noise."""
    if name == "logit":
        return dict(penalty=t.suggest_categorical("penalty", ["l1", "l2"]),
                    C=t.suggest_float("C", 1e-4, 1 if small else 10, log=True))
    if name == "ridge":
        return dict(alpha=t.suggest_float("alpha", 1.0 if small else 1e-2, 1e5, log=True))
    if name == "dtree":
        return dict(max_depth=t.suggest_int("max_depth", 2, 4 if small else 8),
                    min_samples_leaf=t.suggest_int("min_samples_leaf", 100 if small else 50, 3000, log=True))
    if name == "rf":
        return dict(n_estimators=t.suggest_int("n_estimators", 100, 300 if small else 400, step=100),
                    max_depth=t.suggest_int("max_depth", 2 if small else 3, 6 if small else 12),
                    min_samples_leaf=t.suggest_int("min_samples_leaf", 50 if small else 20, 1000, log=True),
                    max_features=t.suggest_categorical("max_features", ["sqrt", 0.5]))
    if name == "macro_gated":
        return dict(
            n_regimes=t.suggest_int("n_regimes", 2, 3 if small else 6),
            C=t.suggest_float("C", 1e-3, 1.0 if small else 50.0, log=True),
            temperature=t.suggest_float("temperature", 0.1, 2.0),
        )
    if small:
        boost = dict(n_estimators=t.suggest_int("n_estimators", 50, 300, step=50),
                     max_depth=t.suggest_int("max_depth", 2, 4),
                     learning_rate=t.suggest_float("learning_rate", 0.01, 0.08, log=True),
                     subsample=t.suggest_float("subsample", 0.5, 0.9),
                     colsample_bytree=t.suggest_float("colsample_bytree", 0.4, 0.9))
    else:
        boost = dict(n_estimators=t.suggest_int("n_estimators", 100, 600, step=100),
                     max_depth=t.suggest_int("max_depth", 2, 8),
                     learning_rate=t.suggest_float("learning_rate", 0.01, 0.2, log=True),
                     subsample=t.suggest_float("subsample", 0.5, 1.0),
                     colsample_bytree=t.suggest_float("colsample_bytree", 0.5, 1.0))
    if name in ("xgb", "lgbm"):
        boost.update(reg_alpha=t.suggest_float("reg_alpha", 1e-3, 10, log=True),
                     reg_lambda=t.suggest_float("reg_lambda", 1e-3, 50 if small else 10, log=True))
        if name == "lgbm":
            boost["min_child_samples"] = t.suggest_int("min_child_samples", 100 if small else 50, 1000, log=True)
        return boost
    if name == "catboost":   # no reg_alpha in CatBoost; L2 is `l2_leaf_reg`
        boost["max_depth"] = min(boost["max_depth"], 8)
        boost["l2_leaf_reg"] = t.suggest_float("l2_leaf_reg", 3.0 if small else 1.0, 30.0 if small else 20.0, log=True)
        return boost
    raise ValueError(name)


def build(name, p, seed=0, n_jobs=-1, firm_cols=None, macro_cols=None):
    """Instantiate a model from its hyperparameter dict.

    firm_cols / macro_cols are required only for name == "macro_gated".
    """
    if name == "logit":
        return make_pipeline(StandardScaler(), LogisticRegression(
            penalty=p["penalty"], C=p["C"], solver="liblinear", max_iter=300))
    if name == "ridge":     # linear-probability model on the binary label
        return make_pipeline(StandardScaler(), Ridge(alpha=p["alpha"]))
    if name == "dtree":
        return DecisionTreeClassifier(random_state=seed, **p)
    if name == "rf":
        return RandomForestClassifier(random_state=seed, n_jobs=n_jobs, **p)
    if name == "xgb":
        return XGBClassifier(tree_method="hist", eval_metric="auc", random_state=seed,
                             n_jobs=n_jobs, verbosity=0, **p)
    if name == "lgbm":
        p = dict(p, num_leaves=min(2 ** p["max_depth"] - 1, 127))
        return LGBMClassifier(subsample_freq=1, random_state=seed, n_jobs=n_jobs, verbose=-1, **p)
    if name == "catboost":
        p = dict(p)
        return CatBoostClassifier(
            iterations=p.pop("n_estimators"), depth=p.pop("max_depth"),
            subsample=p.pop("subsample"), rsm=p.pop("colsample_bytree"),
            bootstrap_type="Bernoulli", random_seed=seed, thread_count=n_jobs,
            verbose=0, allow_writing_files=False, **p)
    if name == "macro_gated":
        if firm_cols is None or macro_cols is None:
            raise ValueError("macro_gated requires firm_cols and macro_cols")
        return RegimeGatedScorer(
            firm_cols=firm_cols, macro_cols=macro_cols,
            n_regimes=p["n_regimes"], C=p["C"],
            temperature=p["temperature"], seed=seed,
        )
    raise ValueError(name)


def score(model, X):
    return model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else model.predict(X)


def monthly_auc(y, s, groups):
    """Mean of the per-group (per decision month) AUC: only the cross-sectional ordering counts. A model that gives a
    whole month one score (e.g. driven by macro level alone) gets 0.5 for that month instead of being rewarded for
    guessing the month's market direction, which is what the pooled AUC over all validation months does."""
    df = pd.DataFrame({"y": np.asarray(y), "s": np.asarray(s), "g": np.asarray(groups)})
    aucs = [roc_auc_score(x.y, x.s) for _, x in df.groupby("g") if x.y.nunique() == 2]
    return float(np.mean(aucs))


def tune(name, Xtr, ytr, Xva, yva, n_trials, seed=0, n_jobs=-1, small=False,
         firm_cols=None, macro_cols=None, groups_va=None):
    """Maximise validation AUC with TPE. Returns (best_params, best_val_auc).

    firm_cols / macro_cols are forwarded to build() for name == "macro_gated".
    groups_va: decision month of each validation row; when given the objective is the mean monthly AUC (matches the
    cross-sectional top-K portfolio), otherwise the AUC pooled over all validation rows.
    """
    def objective(trial):
        m = build(name, suggest(name, trial, small), seed, n_jobs,
                  firm_cols, macro_cols).fit(Xtr, ytr)
        s = score(m, Xva)
        return roc_auc_score(yva, s) if groups_va is None else monthly_auc(yva, s, groups_va)

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=seed))
    study.optimize(objective, n_trials=n_trials)
    return study.best_params, study.best_value

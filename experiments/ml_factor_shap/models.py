"""Model zoo + Optuna search spaces. Every model exposes a scalar score via `score()`."""
import warnings

import numpy as np
import optuna
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
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


def suggest(name, t):
    """Search space per model (the plan's tuning list: depth, lr, n_estimators, subsample,
    colsample, reg_alpha, reg_lambda -- applied wherever the algorithm has the knob)."""
    if name == "logit":
        return dict(penalty=t.suggest_categorical("penalty", ["l1", "l2"]),
                    C=t.suggest_float("C", 1e-4, 10, log=True))
    if name == "ridge":
        return dict(alpha=t.suggest_float("alpha", 1e-2, 1e5, log=True))
    if name == "dtree":
        return dict(max_depth=t.suggest_int("max_depth", 2, 8),
                    min_samples_leaf=t.suggest_int("min_samples_leaf", 50, 3000, log=True))
    if name == "rf":
        return dict(n_estimators=t.suggest_int("n_estimators", 100, 400, step=100),
                    max_depth=t.suggest_int("max_depth", 3, 12),
                    min_samples_leaf=t.suggest_int("min_samples_leaf", 20, 1000, log=True),
                    max_features=t.suggest_categorical("max_features", ["sqrt", 0.5]))
    boost = dict(n_estimators=t.suggest_int("n_estimators", 100, 600, step=100),
                 max_depth=t.suggest_int("max_depth", 2, 8),
                 learning_rate=t.suggest_float("learning_rate", 0.01, 0.2, log=True),
                 subsample=t.suggest_float("subsample", 0.5, 1.0),
                 colsample_bytree=t.suggest_float("colsample_bytree", 0.5, 1.0))
    if name in ("xgb", "lgbm"):
        boost.update(reg_alpha=t.suggest_float("reg_alpha", 1e-3, 10, log=True),
                     reg_lambda=t.suggest_float("reg_lambda", 1e-3, 10, log=True))
        if name == "lgbm":
            boost["min_child_samples"] = t.suggest_int("min_child_samples", 50, 1000, log=True)
        return boost
    if name == "catboost":   # no reg_alpha in CatBoost; L2 is `l2_leaf_reg`
        boost["max_depth"] = min(boost["max_depth"], 8)
        boost["l2_leaf_reg"] = t.suggest_float("l2_leaf_reg", 1.0, 20.0, log=True)
        return boost
    raise ValueError(name)


def build(name, p, seed=0, n_jobs=-1):
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
    raise ValueError(name)


def score(model, X):
    return model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else model.predict(X)


def tune(name, Xtr, ytr, Xva, yva, n_trials, seed=0, n_jobs=-1):
    """Maximise validation AUC with TPE. Returns best params."""
    def objective(trial):
        m = build(name, suggest(name, trial), seed, n_jobs).fit(Xtr, ytr)
        return roc_auc_score(yva, score(m, Xva))

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=seed))
    study.optimize(objective, n_trials=n_trials)
    return study.best_params, study.best_value

---
title: "KOSPI ML Factor Selection: Macro vs Firm Factors with SHAP Interpretability"
slug: kospi-ml-factor-shap-selection
status: tested
origin: "Exploratory study — walk-forward ML factor model on KOSPI large caps (2014-2025). Investigates whether adding macro factors to firm-level fundamental factors improves top-quintile stock selection, and whether tree-based models (LGBM/CatBoost) beat logistic regression in risk-adjusted return. SHAP analysis identifies which factors drive predictions and whether their importance shifts across macro regimes."
origin_gaps: []
tags: [kospi, factor-model, shap, ml-interpretability, macro-factors, fundamental-analysis, walk-forward]
target_venue: ""
novelty_score: 2
priority: 2
pilot_result: "inconclusive — H1 (macro adds over firm-only) not confirmed (all p > 0.3 after Holm); H2 (tree models beat logit in Sharpe) not confirmed (LGBM Δ=+0.09 Sharpe, 95% CI includes 0); H3 (SHAP) confirmed regime-dependence of factor importance (BASE_RATE regime: rank corr=0.79, perm p=0.008). Infrastructure and data pipeline validated. Results limited by small test set (36 months × ~80 stocks)."
failure_reason: ""
linked_experiments:
  - ml-factor-shap-kospi-pilot
date_proposed: "2026-10-22"
date_resolved: ""
---

## Motivation

Classical quantitative factor models for KOSPI assume factor effects are stationary and treat macro variables as background controls. Tree-based ML models can capture non-linear interactions, and SHAP provides post-hoc interpretability. If macro factors contribute marginally over firm-only factors, and if their importance shifts across rate/inflation regimes, that would justify a regime-adaptive factor weighting approach.

## Hypothesis

- **H1**: Adding macro factors (BASE_RATE, TERM_SPREAD, CPI_YOY, VKOSPI, PCR) to firm-level fundamental factors improves monthly top-quintile stock selection AUC and precision on KOSPI (2022-2025 walk-forward test set).
- **H2**: Tree-based models (LGBM, CatBoost) achieve higher risk-adjusted return (Sharpe) than logistic regression on the same factor set.
- **H3**: SHAP global importance rankings shift meaningfully across macro regimes (high vs low BASE_RATE months), indicating regime-dependent factor relevance.

## Approach sketch

Walk-forward experiment (train 2014→test_start, expand annually) on KOSPI top-100 by market cap. Each fold: Optuna hyperparameter tuning → monthly cross-sectional prediction (y=1 if top-quintile excess return) → equal-weight long portfolio of top-20% predicted names → backtest net of 0.20% transaction cost. Factor sets: `firm` (17 fundamental factors) vs `full` (firm + macro). Models: logit, LGBM, CatBoost. SHAP interaction analysis per regime split (BASE_RATE high/low).

## Novelty argument

Low novelty (2/5) — standard ML factor + SHAP pipeline. Main value is as an empirical baseline and data-pipeline foundation for more novel KOSPI quant ideas.

## Target venue

Internal baseline / data infrastructure only.

## Risks

- Small test set (36 months) limits statistical power for H1/H2.
- KOSPI coverage gaps in yfinance fundamentals (unverified accuracy).
- SHAP regime analysis depends on BASE_RATE regime split quality.

## Pilot results

Pilot (A_raw / B_regime / C_regime_q80) results — inconclusive:
- H1 not confirmed: macro vs firm-only AUC differences all within noise (max LGBM prec_k Δ=+0.026, p=0.039 uncorrected, p=0.37 Holm-corrected)
- H2 not confirmed: LGBM Sharpe 1.00 vs logit 0.91, Δ=+0.09, 95% bootstrap CI [-0.25, +0.60]
- H3 confirmed: SHAP regime-dependence significant for BASE_RATE splits (rank corr=0.79, perm p=0.008); DEBT_RATIO shows sign flip across regimes
- Top SHAP factors: RET_3M, VKOSPI, TERM_SPREAD, PCR, DEBT_RATIO

## Lessons learned

- `FinanceDataReader` + `pykrx` combination reliable for KOSPI fundamentals at monthly frequency
- DART filing cache (`opendartreader`) needed for statement-based factors (13 factors)
- Small universe (top-100 mcap) + 36 test months insufficient to distinguish ML models from logit; needs longer test window or broader universe

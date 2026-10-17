# ML factor × macro excess-return experiment (KOSPI/KOSDAQ)

Walk-forward pipeline for the research plan: firm factors + macro → next-month excess-return
classification → tree ensembles vs. linear baselines → top-20 % backtest → SHAP by macro regime.

```bash
pip install -r requirements.txt
# 1) smoke test on synthetic data with a known regime structure (no API keys)
python run_experiment.py --data synthetic --trials 10 --out results/synth
# 2) real data
python fetch_real_data.py prices|macro|fundamentals --out data/real     # UNTESTED, see header
python run_experiment.py --data real --raw-dir data/real --trials 50 --out results/real
python tests/test_lookahead.py                                          # filing-date / macro-lag guards
```

| file | role |
|---|---|
| `config.py` | factor lists, ECOS codes |
| `data_synth.py` | synthetic panel (factor payoffs depend on rate / curve regime, value×quality interaction) |
| `data_real.py` | raw files → panel; fundamentals joined on **filing date**, macro lagged to end of t‑1 |
| `fetch_real_data.py` | FinanceDataReader / pykrx / ECOS / Open DART collectors (untested) |
| `features.py` | target, per-month winsorize (1/99) + rank-gauss or z-score |
| `models.py` | Logit(L1/L2), Ridge, Tree, RF, XGB, LGBM, CatBoost + Optuna spaces |
| `evaluation.py` | AUC, PR-AUC, Precision@20 %, backtest, H1 paired tests, H2 block bootstrap |
| `shap_analysis.py` | SHAP, regime comparison with permutation test, macro×firm interactions |
| `run_experiment.py` | orchestration → `results/<run>/report.md` + csv/png |

## Design decisions to review

- **Walk-forward** is keyed on the year of the *label* month (t+1). For test year Y: tune on
  labels ≤ Y‑2, validate on Y‑1, refit on ≤ Y‑1, predict Y. Fold 1 = train 2014–20 / val 2021 /
  test 2022, as in the plan; no training label is realised after the first test decision date.
- **Target** `y = 1[R_i − R_m > margin]`. The plan's formula was not legible, so `--target-margin`
  defaults to 0 (≈50/50). The plan quotes a 1:4 class ratio; pick a margin that yields it (e.g. 0.03–0.05).
- **Value ratios are ranked on their inverse** (E/P, B/P, CF/P, EBITDA/EV) so negative earnings sort
  to the bottom. Column names stay `PER` etc., so a *positive* SHAP direction for `PER` means *cheap*.
- **Ridge** is a linear-probability model on the binary label (scored by its prediction).
- **Costs**: `0.20 % × Σ|Δw|` per rebalance (first month pays for building the book). Sharpe uses
  rf = 0 and monthly returns × √12. Turnover is one-way (½Σ|Δw|).
- **H1** compares full vs. firm-only per model on monthly AUC / Precision@K (paired one-sided t and
  Wilcoxon). Monthly values are autocorrelated, so treat p-values as indicative. Note that macro
  variables are constant within a month: a *linear* model cannot change its cross-sectional ranking
  with them (the full and firm-only logit results are identical by construction), only models with
  interactions can.
- **H2** is a paired circular-block bootstrap (block = 3 months) of ΔSharpe vs. logistic regression.
- **H3** regimes = macro above/below the median over the *test* months (ex-post description of the OOS
  period, not a model input; a train-median split leaves 2022–25 entirely "high rate"). Reported:
  importance rank correlation, month-level permutation p-value, per-factor direction flips, and
  mean|SHAP interaction| for macro × firm pairs (computed on a random subsample per fold).
- CatBoost is run on numeric features only, so its categorical-feature strength is unused; add
  sector/market as categoricals in `data_real.py` if you want it.

## Known gaps

- The fetchers have never been run; ECOS codes in `config.py`, DART account IDs (`IS_MAP`…) and the
  2y-yield proxy (3y KTB) need checking. VKOSPI is not on ECOS and must be supplied separately.
- Survivorship: the FDR listing only contains currently listed tickers. Add delisted names or the
  backtest is optimistic.
- Per-date administrative-issue flags (`eligible`) need a KRX source.
- Synthetic results validate the code path only; they say nothing about the Korean market.

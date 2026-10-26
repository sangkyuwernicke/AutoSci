[한국어 README](README.ko.md)

# ML factor × macro excess-return experiment (KOSPI/KOSDAQ)

Walk-forward pipeline for the research plan: firm factors + macro → next-month excess-return
classification → tree ensembles vs. linear baselines → top-20 % backtest → SHAP by macro regime.

```bash
pip install -r requirements.txt
# 0) fast profile on synthetic data (100 stocks, from 2020-01-02, train 2020+, test 2023-2025, 15 trials)
python run_experiment.py --quick --out results/quick
# 1) smoke test on synthetic data with a known regime structure (no API keys)
python run_experiment.py --data synthetic --trials 10 --out results/synth
# 2) real data
python prepare_krx.py --krx-dir data/krx --out data/real                       # hand-downloaded KRX files
python fetch_real_data.py macro --out data/real --start-year 2019              # ECOS (+ data/krx/vkospi.csv)
python fetch_real_data.py fundamentals --out data/real --market KOSPI --top-n-mcap 100 --start-year 2019   # DART
python run_experiment.py --quick --data real --raw-dir data/real --out results/q_base
# 3) extended factor set (momentum / reinvestment / forward-looking) and paired comparison
python run_experiment.py --quick --data real --raw-dir data/real --factor-set extended --out results/q_ext
python compare_runs.py results/q_base results/q_ext --labels base extended --out results/base_vs_ext
python prepare_consensus.py vendor_export.csv --out data/real/consensus.parquet --unit 1e6   # optional, vendor data
# 4) tests (offline)
for t in lookahead forward universe krx fetch pilot agent_eval; do python tests/test_$t.py; done
```

| file | role |
|---|---|
| `config.py` | factor lists, ECOS codes |
| `data_synth.py` | synthetic panel (factor payoffs depend on rate / curve regime, value×quality interaction) |
| `data_real.py` | raw files → panel; fundamentals joined on **filing date**, macro lagged to end of t‑1 |
| `prepare_krx.py` | hand-downloaded KRX snapshots / index / VKOSPI csv -> `prices_monthly.parquet`, `index.parquet`, VKOSPI in `macro.parquet` |
| `fetch_real_data.py` | ECOS macro and Open DART fundamentals collectors (untested against live APIs; resumable, call-limited) |
| `universe.py` | financial / SPAC / preferred screens, `exclusions.csv`, statement-coverage filter |
| `prepare_consensus.py` | validates/normalises a vendor point-in-time consensus export → `consensus.parquet` |
| `compare_runs.py` | paired comparison of two runs (base vs extended): monthly AUC / Precision@K / net Sharpe, t, Wilcoxon, block bootstrap |
| `factor_ic.py` | single-factor monthly rank IC vs next-month excess return (see Pilot mode) |
| `pilot_suite.py` | runs factor IC, three pilot configurations and the paired comparison |
| `data_quality.py` | per-factor missing / zero / outlier / coverage report (`data_quality.csv`) |
| `features.py` | target, per-month winsorize (1/99) + rank-gauss or z-score |
| `models.py` | Logit(L1/L2), Ridge, Tree, RF, XGB, LGBM, CatBoost + Optuna spaces |
| `evaluation.py` | AUC, PR-AUC, Precision@20 %, backtest, H1 paired tests, H2 block bootstrap |
| `shap_analysis.py` | SHAP, regime comparison with permutation test, macro×firm interactions |
| `run_experiment.py` | orchestration → `results/<run>/report.md` + csv/png |
| `run_agents.py` | ask TradingAgents for ratings on (stock, month-end) samples -> `predictions.parquet` (see LLM agents section) |
| `compare_agent.py` | agent vs ML models on identical stock-months, with a luck baseline |
| `agent_eval/` | point-in-time data vendor, backends and job runner for TradingAgents |

## Extended factors (`--factor-set extended`)

| group | factors | source / definition |
|---|---|---|
| momentum | `RET_6M`, `MOM_12_1`, `DIST_52W_HIGH` | month-end prices; 12M return skipping the last month; close / 252-day high − 1 |
| reinvestment | `RD_INTENSITY`, `RD_GROWTH` | annual-report R&D ÷ annual sales, YoY R&D growth; usable from the annual filing date; firms with statements but no R&D line get 0 |
| | `CAPEX_INTENSITY`, `ASSET_GROWTH` | TTM PP&E purchases ÷ TTM sales; YoY total-asset growth |
| forward-looking | `FWD_PER` | market cap ÷ 12M-forward consensus net income, (12−m)/12·FY(t) + m/12·FY(t+1) |
| | `FWD_EPS_GROWTH`, `FWD_SALES_GROWTH` | forward estimate vs. trailing-12M actual |
| | `EST_REVISION_3M` | change in the *same fiscal year's* estimate vs. 3 months earlier |

Factors whose inputs are absent are skipped with a warning, so the pipeline runs with or without
`consensus.parquet` / `capex` / R&D.

Look-ahead rules for the new inputs: consensus snapshots are used only if dated ≤ t and ≤ 45 days old
(`consensus_lag_days` in `build_panel` adds a conservative publication lag); free sources (e.g. Naver
Finance) show only the *current* consensus, which would leak today's estimates into history, so a
point-in-time vendor history (FnGuide/DataGuide, Refinitiv) is required. Realised future earnings must
never stand in for estimates. Vendors sometimes back-fill or restate estimates; spot-check a few dates.
R&D is rarely a standard DART line item (`fetch_real_data.py` matches `ifrs-full_ResearchAndDevelopmentExpense`
and Korean name hints) — check coverage in `data_quality.csv` before interpreting `RD_*`.

## Universe

The universe comes from the hand-downloaded month-end KRX snapshots (see below): every stock listed on that
month-end, so names delisted later are included (no survivorship filter). A stock-month is eligible if it is common
stock (code ends in 0), not a SPAC and not a financial (name keywords; add a sector file if you have one). Further
filters in `build_panel` / `run_experiment`:

- `--market KOSPI|KOSDAQ|ALL`: universe and benchmark index are restricted together.
- `--top-n-mcap N`: keep the N largest by market cap each month (point in time).
- `--min-coverage 0.5`: drop stock-months with < 50 % of the 13 statement-based factors (new listings with no
  filing yet) instead of leaving them at the cross-sectional median.
- `--min-mcap-pct x`: drop the smallest x % by market cap each month.
- optional `data/real/exclusions.csv` (`ticker,start,end`): administrative-issue / investment-caution periods,
  which need a KRX KIND download (none is wired in); rows in the window are removed.

`tests/test_universe.py` covers the screening logic offline.

## KRX data downloaded by hand (no automated KRX access)

KRX Data Marketplace forbids automated collection (the pykrx route got an IP blocked), so the KRX inputs are
downloaded from the web screens and converted offline:

```
data/krx/snapshots/*.csv   month-end all-stocks quotes (columns 기준일자,종목코드,종목명,시장구분,종가,...,시가총액,상장주식수)
data/krx/index_kospi.csv   일자,종가   (index_kosdaq.csv optional)
python prepare_krx.py --krx-dir data/krx --out data/real      # -> prices_monthly.parquet, index.parquet
```

Consequences of month-end-only prices: no `VOL_20D` (skipped with a warning), `DIST_52W_HIGH` uses the last 12
month-end closes, and returns are price returns. Snapshot closes are not split-adjusted: when the share count moves
> 10 % while market cap stays within [0.75, 1.33], the month's return is the market-cap change instead. This is a
heuristic (rights issues and mergers can be misread); inspect the "share-count events adjusted" count it prints.
Preferred shares (code not ending in 0), SPACs and financials (name keywords only, no sector file) are excluded.
Stocks that vanish from the snapshots have no delisting return, which biases results slightly upward.
`fundamentals.parquet` and `macro.parquet` still come from `fetch_real_data.py` (DART / ECOS).
`--quick` now means KOSPI only, top-100 by market cap, data from 2020-01-02, train 2020+, test 2023-2025.

## Pilot mode: when the period and the universe cannot grow

With ~36 test months x 100 stocks the mean monthly AUC of a no-skill model has a standard error of about 0.01, so
only AUC gaps of roughly 0.03 or more can be told from noise (`report.md` prints this under "Resolving power").
Treat such a run as an exploratory pilot and read effect sizes and intervals, not p-values. Tools for it:

| tool | what it does |
|---|---|
| `factor_ic.py` | monthly rank IC of every factor vs next-month excess return (mean, Newey-West t, hit rate, per year). `--price-only` uses the whole eligible universe (no DART needed) |
| `--small-data` | shallow, heavily regularised search space; default models only logit, lgbm, catboost (fewer comparisons) |
| `--macro-mode regime` | macro levels become 1 / 0 / 0.5 versus their expanding median (no look-ahead) so trees cannot memorise months; raw levels stay in `*_RAW` for describing SHAP regimes |
| `--target-quantile 0.8` | label = top 20 % by monthly excess return; compare with the margin label (runs with different labels cannot be paired) |
| H1 table | adds a block-bootstrap CI of the mean difference and Holm-adjusted p-values over all model x metric tests |
| `pilot_suite.py` | runs factor_ic, A (raw macro), B (regime macro), C (B + quantile label) and the paired A-vs-B comparison |

```bash
python pilot_suite.py --raw-dir data/real --out-root results/pilot            # --quick profile on real data
python factor_ic.py --data real --raw-dir data/real --price-only --market KOSPI --start-date 2020-01-02
```

## LLM agents (TradingAgents) as an additional "model"

[TradingAgents](https://github.com/TauricResearch/TradingAgents) (Apache-2.0, LangGraph) runs a trading-firm style team of
LLM agents (market / fundamentals analysts, bull-bear debate, trader, risk team, portfolio manager) and returns a
rating for one stock on one date: `Buy / Overweight / Hold / Underweight / Sell` (or `REVIEW` when unparseable).
Here it is used as one more stock-selection method scored with the *same* code as the ML models. The data collection
modules stay as they are; `agent_eval/` feeds their output to TradingAgents instead of the vendors it normally calls.

```
data/real/*.parquet --(agent_eval.store: filing-date / avail-date / month-end as-of)--> "autosci" vendor
     --> TradingAgentsGraph.propagate("005930.KS", "2025-06-30") --> rating --> predictions.parquet (score = rating)
     --> compare_agent.py: same stock-months, same metrics as run_experiment.py + a luck baseline
```

| file | role |
|---|---|
| `agent_eval/store.py` | point-in-time queries on `prices_monthly`, `fundamentals`, `macro` (nothing after `asof`) |
| `agent_eval/vendor.py` | registers vendor `autosci` in TradingAgents' router (`VENDOR_METHODS`; no public API exists, so entries are inserted at run time) |
| `agent_eval/backends.py` | `TradingAgentsBackend` (one fresh graph and memory per decision), `MockBackend` (offline, random ratings) |
| `agent_eval/jobs.py` | choose stocks and months, resumable run (`decisions.jsonl`), ratings -> `predictions.parquet` |
| `run_agents.py` | CLI: `--dry-run` plan, `--backend mock`, `--backend tradingagents --confirm-cost` |
| `compare_agent.py` | agent vs ML on identical stock-months, pre/post LLM-cutoff blocks, permutation luck baseline |

```bash
# separate venv, Python >= 3.11
pip install -r requirements-agents.txt            # TradingAgents + pandas/pyarrow
pip install -r requirements.txt                   # only needed for compare_agent.py (scikit-learn, scipy)
export OPENAI_API_KEY=...                         # or the key of the provider you pass as --llm-provider
COMMON="--raw-dir data/real --market KOSPI --top-n-mcap 100 --start-date 2020-01-02 --n-stocks 20 --test-start 2025 --test-end 2025"
python run_agents.py $COMMON --dry-run                                         # how many decisions? no cost
python run_agents.py $COMMON --backend mock --out results/agents/mock          # plumbing check, no LLM
python run_agents.py $COMMON --backend tradingagents --confirm-cost --max-jobs 2 --out results/agents/run1   # time 2 decisions
python run_agents.py $COMMON --backend tradingagents --confirm-cost --out results/agents/run1               # resumes
python compare_agent.py --agent results/agents/run1 --ml-run results/q_base --ml-fset firm --llm-cutoff 2025-06
```

What the agents see: month-end prices, a monthly technical summary, the latest *filed* statements (TTM ratios, PER / PBR
from the month-end market cap) and the five macro series public by that date. They get **no** news, social or insider
data (none exists in this dataset), so only the `market` and `fundamentals` analysts run by default; daily indicators
(RSI, MACD, ...) are unavailable and the tools say so.

Read the results with these caveats:

- **LLM look-ahead.** A model trained on data covering the test months can recall what happened; the ML pipeline has no
  such leak. Pass `--llm-cutoff` (end of the model's training data) to `compare_agent.py` and trust the "after cutoff"
  block; the other block may reflect memory, not skill. (TradingAgents' README itself only warns that backtest results
  are not reproducible because LLM output and live data vary.)
- **Isolation.** TradingAgents keeps a memory log of settled decisions that feeds later runs. Every decision here gets an
  empty memory file and cache that is deleted afterwards, so no future outcome can reach an earlier decision.
- **Small samples.** 20 stocks x 12 months is ~240 decisions (each a full multi-agent run: many LLM calls; measure the
  cost of two before launching more). The top-20 % portfolio holds ~4 names. `compare_agent.py` therefore compares the
  agent with a permutation null of its own scores (`auc_null_p95`): an uninformed rater scored 0.52 AUC on 15 stocks
  in a test of the plumbing, so differences of a few hundredths mean nothing.
- **Ties and noise.** Five rating levels tie often; ties are broken by a seeded random jitter. LLM output varies run to
  run (`--repeats` averages independent runs). TradingAgents scores its own decisions over a 5-trading-day
  holding period by default (`holding_period_days`); the monthly label here is not what it was built to predict.
- **Not covered.** No Optuna, no SHAP (H3), no macro on/off comparison (H1): there is no trained model to explain.
- **Not tested here:** the adapter was verified offline against the real TradingAgents v0.7.0 router and graph
  construction (`tests/test_agent_eval.py`), but not with a live LLM; the first real decision may need adjustments.

## Design decisions to review

- **Walk-forward** is keyed on the year of the *label* month (t+1). For test year Y: tune on labels <= Y-2,
  validate on Y-1, refit on <= Y-1, predict Y. Fold 1 = train 2014-20 / val 2021 / test 2022, as in the plan; no
  training label is realised after the first test decision date.
- **Target** `y = 1[R_i - R_m > margin]`; with `--target-quantile 0.8` the top 20 % by monthly excess return are
  positive (fixed 1:4 every month, independent of market direction; exclusive with margin). The plan's formula was
  not legible, so `--target-margin` defaults to 0 (about 1:1). Use the quantile label for the plan's 1:4 ratio.
- **Value ratios are ranked on their inverse** (E/P, B/P, CF/P, EBITDA/EV) so negative earnings sort to the
  bottom. Column names stay `PER` etc., so a *positive* SHAP direction for `PER` means *cheap*.
- **Ridge** is a linear-probability model on the binary label (scored by its prediction).
- **Costs**: `0.20 % x sum|dw|` per rebalance (first month pays for building the book). Sharpe uses rf = 0 and
  monthly returns x sqrt(12). Turnover is one-way (0.5 x sum|dw|).
- **H1** compares full vs. firm-only per model on monthly AUC / Precision@K (paired one-sided t and Wilcoxon).
  Monthly values are autocorrelated, so treat p-values as indicative. Macro variables are constant within a
  month, so a *linear* model cannot change its cross-sectional ranking with them (only the firm-factor
  coefficients move slightly when it is refit); only models with interactions can use macro information.
- **H2** is a paired circular-block bootstrap (block = 3 months) of the Sharpe difference vs. logistic regression.
- **H3** regimes = macro above/below the median over the *test* months (ex-post description of the OOS period, not
  a model input; a train-median split would leave 2022-25 entirely "high rate"); ties at the median fall back to
  `>=`. Reported: importance rank correlation, month-level permutation p-value, per-factor direction flips, and
  mean|SHAP interaction| for macro x firm pairs (computed on a random subsample per fold).
- CatBoost is run on numeric features only, so its categorical-feature strength is unused; add sector/market as
  categoricals in `data_real.py` if you want it.

## Troubleshooting

- Do not scrape KRX (pykrx, FinanceDataReader's KRX endpoints): the KRX Data Marketplace terms forbid automated
  collection and the IP gets blocked. Use screen downloads, a data product, or the official KRX Open API.
- `No module named 'OpenDartReader'`: the package `opendartreader` >= 0.3 is imported as `opendartreader`
  (the code handles both). `pip install -r requirements.txt` first.
- DART is called ~28 times per ticker for 2019-2025; `--max-calls` (default 6000) stops runs that would exceed a
  sane daily quota. Results are cached per ticker in `data/real/dart_cache/`, so reruns only fetch what is missing.
- VKOSPI: download the VKOSPI daily close from KRX to `data/krx/vkospi.csv` (일자,종가); `fetch_real_data.py macro`
  or `prepare_krx.py` then adds it to `macro.parquet`.

## Known gaps

- The ECOS and DART collectors have never been run against the live APIs; ECOS series codes in `config.py`, DART
  account IDs (`IS_MAP`...) and the 2y-yield proxy (3y KTB) need checking on the first run.
- Month-end KRX snapshots only: no daily series (no `VOL_20D`), unadjusted closes patched by a share-count heuristic,
  and no delisting returns for stocks that disappear.
- Financials are screened by name keywords (no sector file); administrative-issue / investment-caution periods need
  a KRX KIND download for `exclusions.csv`.
- Point-in-time analyst consensus is not freely available; without it the four forward-looking factors are skipped.
- Synthetic results validate the code path only; they say nothing about the Korean market.

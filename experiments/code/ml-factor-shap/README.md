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
# 3b) news-sentiment factors (KR-FinBert-SC) and paired comparison against the run without them
python build_news_sentiment_panel.py --method model --out-dir data/news/sentiment_cmp/finbert
python prepare_sentiment.py --in-dir data/news/sentiment_cmp --out data/real
python run_experiment.py --quick --data real --raw-dir data/real --sentiment finbert --test-end 2025 --out results/q_sent_finbert
python compare_runs.py results/q_base results/q_sent_finbert --labels base finbert --out results/base_vs_finbert
python factor_ic.py --data real --raw-dir data/real --market KOSPI --start-date 2017-01-01 --end-date 2025-12-31 \
    --sentiment finbert --residualize-on RET_1M RET_3M VOL_20D mcap --out results/ic_sent   # IC raw and net of controls
python daily_sentiment_ic.py --out results/daily_sentiment      # daily rank IC + long-short book by year, entry timing A / B
python weekly_sentiment_ic.py --out results/weekly_sentiment    # 5-day signal, 5-day hold, five rebalance phases
python make_summary_table.py --none results/q_base --finbert results/q_sent_finbert --out results/summary   # see its row below
# 4) tests (offline)
for t in lookahead forward universe krx fetch pilot macro_gated target_impute topk tune_metric sentiment daily_sentiment weekly_sentiment summary_table; do python tests/test_$t.py; done
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
| `build_news_sentiment_panel.py` | BigKinds yearly xlsx → per-KOSPI-stock daily news sentiment with KR-FinBert-SC (`--method model`, default) |
| `compare_sentiment_methods.py` | lexicon vs KR-FinBert study (not part of the experiment): agreement, next-day / 5-day rank IC. Its daily IC enters at the last trading day's close on or before the news date (weekend news enters before it exists), so treat it as an upper bound; `daily_sentiment_ic.py` replaces it for timing-clean numbers |
| `prepare_sentiment.py` | daily FinBert panel → `data/real/sentiment_finbert.parquet` for `--sentiment` |
| `sentiment.py` | daily ticker × date sentiment → month-end factors (trailing windows, lagged, no look-ahead) |
| `daily_sentiment_ic.py` | daily rank IC and daily long-short / long-only books by year; news rolled to the next trading day; entry A (same-day close, optimistic) vs B (next-day close, tradable); costs on sum\|dw\| |
| `weekly_sentiment_ic.py` | same at a weekly horizon: 5-trading-day trailing signal, 5-day hold, averaged over the five rebalance phases |
| `analyze_auc_sources.py` | where a model's AUC comes from: monthly AUC of the score after removing volatility, size, reversal, momentum, value and quality month by month, plus single-factor AUC and correlation with the score (`results/v18_auc_sources/`) |
| `make_summary_table.py` | Firm × Macro × Sentiment table (Panel A: per-model AUC / net Sharpe from two runs' `predictions.parquet`, pooled effects with block-bootstrap CI; Panel B: sentiment IC). Models are read from the data (7-model `--quick` or `--small-data` pairs both work); `--top-q 200` for the whole-KOSPI book of 200 stocks; Panel B takes `--ic <factor_ic dir>=<label> ...` (default: the `--quick` top-100/200 runs) |
| `compare_runs.py` | paired comparison of two runs (base vs extended): monthly AUC / Precision@K / net Sharpe, t, Wilcoxon, block bootstrap |
| `factor_ic.py` | single-factor monthly rank IC vs next-month excess return (see Pilot mode); `--sentiment`, `--end-date`, `--residualize-on` for the sentiment factors, `avg_n` = stocks behind each IC |
| `pilot_suite.py` | runs factor IC, three pilot configurations and the paired comparison |
| `data_quality.py` | per-factor missing / zero / outlier / coverage report (`data_quality.csv`) |
| `features.py` | target, per-month winsorize (1/99) + rank-gauss or z-score |
| `models.py` | Logit(L1/L2), Ridge, Tree, RF, XGB, LGBM, CatBoost + Optuna spaces |
| `evaluation.py` | AUC, PR-AUC, Precision@20 %, backtest, H1 paired tests, H2 block bootstrap |
| `shap_analysis.py` | SHAP, regime comparison with permutation test, macro×firm interactions |
| `run_experiment.py` | orchestration → `results/<run>/report.md` + csv/png |

## News-sentiment factors (`--sentiment finbert`)

Opt-in. Appended to the firm factors, so Firm-only vs Firm+Macro both include them; measure their effect by
pairing a run with `--sentiment none` against one without (`compare_runs.py`). Source: Maeil Business (매일경제)
securities section via BigKinds, matched to KOSPI common stocks by name; only title + 200-char summary.

| factor | definition (window ends at month-end − `--sentiment-lag-days`, default 1) |
|---|---|
| `SENT_MEAN_1W` / `_1M` / `_3M` | article-weighted mean score over the last 7 / 30 / 90 days |
| `SENT_CHG` | `SENT_MEAN_1W` − mean over the 23 days before it (short-term change of tone) |
| `SENT_STD_1M` | std of the per-day mean scores over 30 days (≥ 3 news-days) |
| `NEWS_COUNT_1M` | log(1 + articles in 30 days); 0 = no news |

No news is **missing**, never 0 or the previous month: these columns skip `impute_ffill` and `--max-missing` and are
median-imputed after the monthly rank transform. Coverage is sparse (KOSPI top-100, 2021+: 58 % of stock-months have
news in 30 days, `SENT_MEAN_1W` 28 %, `SENT_STD_1M` 25 %), so the weekly/change/dispersion factors are mostly imputed.
News ends 2025-12-31: keep `--test-end 2025` (a warning is printed otherwise; later months look like "no news").

### Evidence so far (`results/v16_*`, `v17_*`; exploratory, not corrected for multiple comparisons)

- **Monthly model, whole KOSPI** (~620 stocks, hold 200, 72 test months 2020-2025): monthly AUC with vs without
  FinBert differs by -0.005 to +0.005, every paired CI contains 0. Net Sharpe is higher in all six cells
  (mean +0.04) but not significant once six comparisons are accounted for.
- **Single-factor monthly IC** (whole KOSPI): `SENT_*` |t| <= 1.5. `NEWS_COUNT_1M` looks significant after removing
  volatility and reversal (+0.044, t 5.4) but is a size proxy (+0.006, t 1.0 once market cap is removed too).
- **Daily** (`daily_sentiment_ic.py`): rank IC 0.02-0.04 with same-day entry (A), about 0 with next-day entry (B).
  The daily long-short book turns over ~3.6 of a maximum 4 each day, so cost 0.2% x sum|dw| exceeds the gross
  return in every year. Number of stocks with news per day: ~18.
- **Weekly** (`weekly_sentiment_ic.py`): net Sharpe positive only in 2025 (+0.3 to +0.5; across rebalance phases
  -0.3 to +1.3), negative in 2020-2024, and negative for the top-200 by market cap even in 2025 (the 2025 gain
  looks concentrated in small caps, where real costs are higher; not verified).
- **Scorer quality** (lexicon -> FinBert changed article labels a lot, kappa 0.28) left the monthly results unchanged;
  other scorers (e.g. an LLM) are untested, and any LLM run needs a look-ahead check because its training data
  covers 2015-2025.

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
- **`--quick` vs `--top-k`:** `--quick` keeps ~91 stocks per month but `--top-k` defaults to 200, so every model holds
  the whole universe and CAGR / Sharpe / MDD / Precision@K in `report.md` and `metrics.csv` are identical across
  models (a warning is printed and written into `report.md`). Use `--top-k 20`, or compare AUC and
  `compare_runs.py` (it re-selects the top 20 % from the stored scores). The original design is the whole KOSPI
  (`--top-n-mcap 0`, ~650 stocks) holding 200 against the official KOSPI200 equal-weight index.
- **News data:** one outlet (Maeil Business securities section) via BigKinds, title + 200-character summary, publication
  date only (no time of day, which is why daily results are shown with entry timing A and B), ends 2025-12-31.

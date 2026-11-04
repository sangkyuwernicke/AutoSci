# ML factor × macro excess-return experiment (KOSPI/KOSDAQ)

Walk-forward pipeline for the research plan: firm factors + macro → next-month excess-return
classification → tree ensembles vs. linear baselines → top-20 % backtest → SHAP by macro regime.

```bash
pip install -r requirements.txt
# 0) fast profile (KOSPI top-100, from 2020-01-02, train 2020+, test 2023-2025, 15 trials; flags override)
python run_experiment.py --quick --out results/quick
# 1) smoke test on synthetic data with a known regime structure (no API keys)
python run_experiment.py --data synthetic --trials 10 --out results/synth
# 2) real data
python prepare_krx.py --krx-dir data/krx --out data/real                # hand-downloaded KRX files
python fetch_real_data.py macro --out data/real --start-year 2019              # ECOS (+ data/krx/vkospi.csv)
python fetch_real_data.py fundamentals --out data/real --market KOSPI --top-n-mcap 100 --start-year 2019   # DART
python run_experiment.py --data real --raw-dir data/real --trials 50 --out results/real
python tests/test_lookahead.py                                          # filing-date / macro-lag guards
python compare_runs.py results/base results/ext --labels base extended --out results/base_vs_ext   # paired tests
python tests/test_forward.py                                            # consensus / R&D / momentum guards
# extended factor set (adds forward-looking + reinvestment + momentum factors)
python prepare_consensus.py vendor_export.csv --out data/real/consensus.parquet --unit 1e6
python run_experiment.py --data real --raw-dir data/real --factor-set extended --min-mcap-pct 5 --out results/real_ext
```

| file | role |
|---|---|
| `config.py` | factor lists, ECOS codes |
| `data_synth.py` | synthetic panel (factor payoffs depend on rate / curve regime, value×quality interaction) |
| `data_real.py` | raw files → panel; fundamentals joined on **filing date**, macro lagged to end of t‑1 |
| `prepare_krx.py` | hand-downloaded KRX snapshots / index / VKOSPI csv -> `prices_monthly.parquet`, `index.parquet`, VKOSPI in `macro.parquet` |
| `fetch_real_data.py` | ECOS macro and Open DART fundamentals collectors (untested against live APIs; resumable, call-limited) |
| `prepare_consensus.py` | validates/normalises a vendor point-in-time consensus export → `consensus.parquet` |
| `compare_runs.py` | paired comparison of two runs (base vs extended): monthly AUC / Precision@K / net Sharpe, t, Wilcoxon, block bootstrap |
| `data_quality.py` | per-factor missing / zero / outlier / coverage report (`data_quality.csv`) |
| `features.py` | target, per-month winsorize (1/99) + rank-gauss or z-score |
| `models.py` | Logit(L1/L2), Ridge, Tree, RF, XGB, LGBM, CatBoost + Optuna spaces |
| `evaluation.py` | AUC, PR-AUC, Precision@20 %, backtest, H1 paired tests, H2 block bootstrap |
| `shap_analysis.py` | SHAP, regime comparison with permutation test, macro×firm interactions |
| `run_experiment.py` | orchestration → `results/<run>/report.md` + csv/png |

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

- The fetchers have never been run; ECOS codes in `config.py`, DART account IDs (`IS_MAP`…) and the
  2y-yield proxy (3y KTB) need checking. VKOSPI is not on ECOS and must be supplied separately.
- Survivorship: the FDR listing only contains currently listed tickers. Add delisted names or the
  backtest is optimistic.
- Per-date administrative-issue flags (`eligible`) need a KRX source.
- Synthetic results validate the code path only; they say nothing about the Korean market.

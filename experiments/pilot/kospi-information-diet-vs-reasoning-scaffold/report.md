# Pilot Verdict Report: kospi-information-diet-vs-reasoning-scaffold

## Verdict: PASS

## Results Summary

| Cell | Cumulative Return | Sharpe | MDD | Parse-failure rate | LLM calls |
|---|---|---|---|---|---|
| D1_S0 | 3.65% | 6.31 | -2.04% | 6.7% | 16 |
| D1_S3 | 2.71% | 7.39 | -1.19% | 0% | 112 |
| D5_S0 | 2.58% | 4.73 | -2.32% | 0% | 15 |
| D5_S3 | 2.47% | 8.01 | -0.98% | 0% | 105 |
| **Buy & Hold (benchmark, 0 LLM calls)** | **3.78%** | 3.71 | — | — | 0 |

Derived (diagnostic only, 1 seed / 5 days / 3 names — not statistically powered):
- ΔData(S0) = D5_S0 − D1_S0 = -1.07pp
- ΔScaffold(D1) = D1_S3 − D1_S0 = -0.94pp
- ΔScaffold(D5) = D5_S3 − D5_S0 = -0.11pp

## Pilot Log
- Log: `experiments/pilot/code/kospi-information-diet-vs-reasoning-scaffold/pilot.log`
- Key signals: clean run, no crashes. One expected, gracefully-handled warning — pykrx has no per-ticker investor-flow data for KODEX 200 (ETF), confirmed as a genuine KRX/pykrx data-availability gap, not a bug (D5 for KODEX 200 falls back to news+technical only).

## Success-criterion check (against `experiments/pilot/kospi-information-diet-vs-reasoning-scaffold.yaml`)
- All 4 cells complete without crashing: **met**
- Parse-failure rate < 10% in every cell: **met** (max 6.7%, D1_S0)
- Qualitative trace confirms S3 responds to debate/analyst content: **met** — e.g. D5_S3 trader/risk stages visibly change position size in response to "foreign investor selling" from the macro-flow analyst
- Qualitative trace confirms D5 decisions reference DART/flow content: **met** — analysts correctly show `input_present=True` for DART/flow on D5, `input_present=False` on D1 (channels are structurally distinct as designed)
- No cell degenerate: **met** (after fixing a HOLD-weight bug that zeroed D5_S0 in the first full run — see below)

## Bugs found and fixed during this pilot
1. `.env` relative-path bug in `tools/_env.py` — silently loaded empty API keys when run from the pilot's own subdirectory (also affects the sibling pilot's identical import pattern, not fixed there). Fixed via a temporary `chdir` in `run_pilot.py`.
2. HOLD-decision weight bug in `backtest.py` — treated HOLD as "freeze at previous realized weight" instead of using the agent's own stated `position_fraction`, silently zeroing any name whose first decision was HOLD. Caused the D5_S0 cell to return exactly 0.0 in the first full run. Fixed; re-run confirmed non-degenerate results across all 4 cells.
3. OpenRouter 429 rate-limiting mis-attributed as JSON parse failures — added backoff-retry specific to HTTP 429, separate from the parse-failure retry path.
4. DART body-content extraction (post-pilot follow-up, not yet re-run through the full LLM pipeline): noise-filtered routine filing types (96 → 24 substantive filings for Samsung) and fixed a `<style>`-block-strips-to-garbage bug in the plain-text extraction. Verified at the data layer only.

## Wiki Changes

| Page | Field | Old | New |
|---|---|---|---|
| ideas/kospi-information-diet-vs-reasoning-scaffold | pilot_result | "" | "pass — 4 cells completed cleanly with 0-6.7% JSON parse-failure ... infrastructure validated, sample too small to test H1/H2, proceed to full study" |
| ideas/kospi-information-diet-vs-reasoning-scaffold | status | proposed | proposed (unchanged — pass does not transition status) |

## Next Steps
- Proceed to `/exp-design` to scope the full study (15 KOSPI large caps + KODEX 200, 2024-01 → 2026-08 walk-forward, 5 seeds per cell).
- Before the full run, decide whether to carry forward the DART body-content improvements (noise filter + style-strip fix) — verified at the data layer but not yet re-run through the LLM pipeline.
- Korean-language bulk news source (BigKinds/AI-Hub/Naver) is still the critical open dependency for the full study — the pilot used a hand-curated ~5-headline stub, not a bulk pipeline.

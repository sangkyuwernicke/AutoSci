---
name: "CoT-Based LLM ETF Allocation Framework"
slug: cot-based-llm-etf-allocation-framework
type: prompting
tags:
  - llm
  - chain-of-thought
  - portfolio-management
  - etf
  - finance
  - news-analysis
source_papers:
  - "[[etf-asset-allocation-strategy-using-chatgpt]]"
parent_methods: []
child_methods: []
realizes_concepts:
  - "[[chain-thought-prompting-financial-text-analysis]]"
code_repo: ""
date_updated: 2026-05-29
---

## Problem setting

Given a corpus of economic news headlines (batch-level, 1–4 week windows), produce a rebalanceable ETF sector-weight vector that reflects market sentiment and sector-level outlook without requiring fine-tuning or numerical price data.

## Mechanism

A two-stage CoT prompting pipeline:

- **Task1 (Keyword Extraction + Sector Mapping)**: Takes a batch of headlines as input; outputs a JSON array of 30 top keywords, each annotated with sector label (one of 11 fixed KRX categories), frequency count, and a contextual detail field. The CoT constraint forces reasoning about signal direction, intensity, recurrence, and contextual coherence before the keyword is sector-assigned.

- **Task2 (Allocation Generation)**: Takes Task1's structured keyword-sector summary as input; outputs a `sector_allocations` JSON array (sector, allocation %, two-to-three sentence rationale) plus an overall `investment_strategy` field. Hard constraints enforced via the prompt: weights sum to 100%, no negative allocations, each rationale must cite specific keywords from Task1.

## Procedure

1. Collect and preprocess news headlines (remove irrelevant articles by tag).
2. Group into rebalancing windows (1-week, 2-week, 4-week).
3. For 4-week batches, randomly sample 3,000 rows to fit token limits.
4. Call Task1 prompt → parse JSON → verify schema.
5. Pass Task1 output to Task2 prompt → parse JSON → verify schema.
6. Repeat steps 4–5 twenty times per text dataset; average the allocation vectors.
7. Apply allocation vector to a universe of sector ETFs; rebalance at period end.
8. Evaluate performance (return, Sharpe, MDD) against benchmarks.

## Assumptions

- News headlines are sufficiently informative for sector-level portfolio allocation.
- The LLM's pretraining encodes adequate financial domain knowledge for zero-shot sector classification.
- Averaging 20 independent runs reduces non-deterministic variance to acceptable levels.
- Sector ETFs adequately span the exposure implied by the news signals.

## Limitations

- Token-limit sampling (4-week batches capped at 3,000 rows) may discard informative headlines.
- The 11-sector taxonomy is fixed to KRX ETF availability; may not transfer to other markets.
- No look-ahead-bias guard: news timestamps vs. price data alignment must be verified.
- Transaction costs and slippage not accounted for.

## Tradeoff profile

| Dimension | Assessment |
|---|---|
| Interpretability | High — JSON schema forces explicit sector reasoning |
| Cost | Moderate — 20 API calls per window × number of rebalancing periods |
| Latency | Moderate — suitable for weekly/monthly rebalancing, not intraday |
| Domain specificity | Medium — prompt-engineered for KRX sectors; requires re-prompting for other markets |
| Generalization | Untested outside Korea, H1 2024 |

## Evaluated by

- [[etf-asset-allocation-strategy-using-chatgpt]] — 6-month backtest on Korean sector ETFs, H1 2024.

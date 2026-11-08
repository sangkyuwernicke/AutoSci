---
title: "RAG vs Pure Chain-of-Thought for the Korean ETF Allocator Across Market Regimes"
slug: kospi-etf-allocator-rag-vs-cot-ablation
status: failed
origin: "ideate: the CoT ETF allocation paper explicitly lists 'how would RAG integration compare to pure CoT' and 'does the framework hold in bear/sideways regimes' as future work — ablate a retrieval-augmented variant of the two-stage Korean CoT pipeline across the 2024 rally and 2026-07 crash"
origin_gaps:
  - "[[chain-thought-prompting-financial-text-analysis]]"
  - "[[llm-finance]]"
tags:
  - kospi
  - chain-of-thought
  - retrieval-augmented-generation
  - etf-allocation
  - regime-robustness
target_venue: ""
novelty_score: ""
priority: 1
pilot_result: ""
failure_reason: "[filter] Single-framework, incremental study explicitly scoped as future work by the source paper ([[etf-asset-allocation-strategy-using-chatgpt]]). A RAG-vs-CoT ablation on one Korean prompting pipeline, even extended across regimes, is thin for a standalone venue. Subsumed as one ablation axis (the D2/D3 Korean-news and disclosure channels) inside the broader [[kospi-information-diet-vs-reasoning-scaffold]] transfer study, where it contributes to a larger claim."
linked_experiments: []
date_proposed: 2026-08-31
date_resolved: 2026-08-31
---

## Motivation

The [[cot-based-llm-etf-allocation-framework]] was tested only in the H1-2024 bull market with a fixed zero-shot CoT policy and no retrieval grounding. The source paper names both "RAG vs pure CoT" and "bear/sideways regimes" as open questions, and [[chain-thought-prompting-financial-text-analysis]] lists "combining CoT with RAG for factual grounding of sector signals" as an open problem.

## Hypothesis

Adding retrieval of historical sector-performance context to the two-stage Korean CoT ETF pipeline improves allocation Sharpe over pure CoT, and the gap widens in bear/sideways regimes where zero-shot sector priors are least reliable.

## Approach sketch

Reimplement the two-stage pipeline (Korean headlines -> keyword/sector extraction -> ETF weights). Ablate: pure CoT vs CoT + RAG over past sector returns and past allocation outcomes. Evaluate across pre-registered 2024 rally / 2026-07 crash / recovery windows on KRX 11-sector ETFs with transaction costs.

## Novelty argument

Directly sanctioned as future work by the source paper, which makes it a natural follow-up but a narrow one — one pipeline, one added component.

## Target venue

N/A — eliminated at Phase 3 first-pass filter.

## Risks

RAG can inject noise from irrelevant retrieved context; contribution is small on its own.

## Pilot results

N/A — eliminated at Phase 3 first-pass filter.

## Lessons learned

(empty)

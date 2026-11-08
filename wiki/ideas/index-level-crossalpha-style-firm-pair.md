---
title: "Index-Level CrossAlpha-Style Firm-Pair Graph Adaptation for KOSPI-NASDAQ Correlation"
slug: index-level-crossalpha-style-firm-pair
status: failed
origin: "ideate: Review LLM Phase 2 brainstorm candidate — adapt CrossAlpha's disclosure-derived firm-pair graph mechanism from firm-level cross-market factor prediction down to index-level KOSPI-NASDAQ correlation analysis for an LLM trading agent."
origin_gaps:
  - "[[llm-multi-agent-financial-trading]]"
  - "[[agentic-trading]]"
tags:
  - kospi
  - cross-market-correlation
  - firm-pair-graph
  - transfer
target_venue: ""
novelty_score: ""
priority: 1
pilot_result: ""
failure_reason: "[filter] CrossAlpha (arXiv 2605.29286, 2026) already establishes the disclosure-based cross-market firm-pair graph mechanism across five markets including Korea, using annual-report-derived firm similarity to predict target-market firm returns from source-market signals. Narrowing that mechanism's scope to KOSPI-NASDAQ index-level correlation (rather than firm-level disclosure similarity) is a scope reduction of an already-published method, not a new signal, mechanism, or formulation — insufficient novelty delta for a standalone contribution. The mechanistic-exposure angle this idea was reaching for (index co-movement driven by a small number of globally-exposed constituents) is already captured more directly and more cheaply by [[global-linkage-channel-ablation-blanket-index]]'s concentration-weighted D6b channel, which does not require adapting CrossAlpha's disclosure-graph infrastructure at all."
linked_experiments: []
date_proposed: 2026-09-21
date_resolved: 2026-09-21
---

## Motivation

CrossAlpha (arXiv 2605.29286) builds a cross-market firm-pair graph from annual-report disclosure similarity to predict target-market firm returns from source-market signals, evaluated across US/Japan/Taiwan/Korea/Hong Kong. One could imagine adapting its graph-construction mechanism to operate at the index level — building a KOSPI-NASDAQ "index-pair" analog — as the basis for a global-linkage channel in a KOSPI LLM trading agent.

## Hypothesis

An index-level adaptation of CrossAlpha's disclosure-derived firm-pair graph mechanism would provide a more informative cross-market correlation signal for KOSPI trading agents than a naive statistical index-correlation baseline.

## Approach sketch

Reimplement CrossAlpha's Disclosure Distillation and Residual Schema Graph Construction components at index level (or aggregate firm-level scores up to an index-level composite); feed the resulting signal into a KOSPI trading agent; compare against blanket KOSPI-NASDAQ statistical correlation.

## Novelty argument

This is fundamentally a scope-narrowed reapplication of CrossAlpha's already-published mechanism (disclosure-similarity firm-pair graphs), not a new signal or formulation. The concentration/exposure-weighted angle this idea was implicitly reaching for — that a small number of globally-exposed KOSPI constituents (Samsung, SK Hynix) drive the observed index-level co-movement — is already captured directly, and far more cheaply (no disclosure-graph infrastructure needed), by [[global-linkage-channel-ablation-blanket-index]]'s D6b mechanistic channel.

## Target venue

N/A — eliminated at Phase 3 first-pass filter.

## Risks

Too close to an existing published mechanism (CrossAlpha); would require substantial reformulation to differentiate, and the differentiation it was reaching for is already served by a cheaper sibling idea.

## Pilot results

N/A — eliminated at Phase 3 first-pass filter.

## Lessons learned

(empty)

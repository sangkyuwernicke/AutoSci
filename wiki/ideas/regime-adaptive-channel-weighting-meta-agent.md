---
title: "Regime-Adaptive Channel-Weighting Meta-Agent for KOSPI Cross-Market Signals"
slug: regime-adaptive-channel-weighting-meta-agent
status: failed
origin: "ideate: Review LLM Phase 2 brainstorm candidate — a meta-agent that dynamically adjusts the weight given to the global-linkage (NASDAQ-correlation) channel based on a detected market regime, rather than treating the channel as a fixed additive input."
origin_gaps:
  - "[[agentic-trading]]"
  - "[[llm-multi-agent-financial-trading]]"
tags:
  - kospi
  - cross-market-correlation
  - regime-detection
  - meta-agent
target_venue: ""
novelty_score: ""
priority: 1
pilot_result: ""
failure_reason: "[filter] Subsumed by [[global-linkage-channel-ablation-blanket-index]], which already pre-registers regime-dependence (H3) as a moderator test on the channel's marginal value, computed directly from the study's own rolling KOSPI-NASDAQ correlation series — no separate adaptive-weighting mechanism is needed to answer that question. A dedicated meta-agent that dynamically reweights the channel is an orchestration-side refinement, not an independent research contribution, and it substantially duplicates the mechanism of the already-active wiki idea [[kospi-regime-adaptive-dag-rl-trading]] (an RL meta-agent that switches orchestration topology per detected regime) — the only difference is switching a channel weight instead of a DAG topology, which is not a large enough conceptual delta to justify a separate idea page at this stage."
linked_experiments: []
date_proposed: 2026-09-21
date_resolved: 2026-09-21
---

## Motivation

If a global-linkage / cross-market-correlation channel is added to a KOSPI LLM trading agent (see [[global-linkage-channel-ablation-blanket-index]]), its value plausibly varies with the market's correlation regime (e.g. the 2026 KOSPI-NASDAQ correlation spike vs. the historical low-correlation baseline). One could imagine a meta-agent that detects the regime and dynamically up- or down-weights the channel accordingly, rather than treating the channel as a fixed additive input across the whole backtest.

## Hypothesis

A regime-adaptive channel-weighting meta-agent that dynamically adjusts the global-linkage channel's weight based on a detected correlation regime will outperform a fixed-weight (always-on) global-linkage channel.

## Approach sketch

Detect the rolling KOSPI-NASDAQ correlation regime (e.g. low/medium/high tercile of the trailing 60-day correlation); train or hand-design a lightweight controller (contextual bandit or rule-based gate) that scales the global-linkage channel's influence on the trader agent up in high-correlation regimes and down in low-correlation regimes; compare against the fixed-weight D6 channel from the sibling idea.

## Novelty argument

The regime-dependence question this meta-agent would answer is already directly tested by [[global-linkage-channel-ablation-blanket-index]]'s H3 (does the channel's marginal value change across regimes), without requiring a separate adaptive-weighting architecture. Adding a dynamic controller on top answers "should the weight be adaptive" only after "does the channel matter, and does its value vary by regime" is already established — premature architecture before the underlying finding is confirmed. It also closely mirrors [[kospi-regime-adaptive-dag-rl-trading]]'s existing mechanism (regime-conditioned meta-agent switching), differing only in what is being switched (a channel weight vs. an orchestration DAG).

## Target venue

N/A — eliminated at Phase 3 first-pass filter (folded into [[global-linkage-channel-ablation-blanket-index]]'s H3 as a regime-moderator test rather than pursued as its own architecture).

## Risks

Would duplicate [[kospi-regime-adaptive-dag-rl-trading]]'s core mechanism if pursued independently; premature relative to establishing the underlying channel-value finding first.

## Pilot results

N/A — eliminated at Phase 3 first-pass filter.

## Lessons learned

(empty)

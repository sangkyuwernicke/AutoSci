---
title: "Process Reward Model Transfer from Math Reasoning to KOSPI Trade Step Verification"
slug: transfer-triple-barrier-rl-kospi-price
status: failed
origin: "ideate: Transfer process reward model (PRM) mechanism from math reasoning to KOSPI trading intermediate step quality scoring"
origin_gaps:
  - "[[agentic-trading]]"
  - "[[llm-finance]]"
tags:
  - rl
  - llm
  - kospi
  - process-reward-model
  - reward-shaping
target_venue: ""
novelty_score: ""
priority: 1
pilot_result: ""
failure_reason: "[filter] Trade-R1 (arxiv 2601.03948, January 2026) directly addresses process-level reward verification for stochastic trading environments. GIFT (arxiv 2606.08450, June 2026) proposes LLM-guided reward shaping for financial RL. The core contribution — scoring intermediate trading reasoning steps with a trained reward model — is already covered by these papers. A KOSPI-specific Korean PRM would require annotating Korean trading reasoning traces, which is a data collection project, not a research contribution."
linked_experiments: []
date_proposed: 2026-07-21
date_resolved: 2026-07-21
---

## Motivation

GRPO and PPO use outcome-only rewards (final portfolio return), which are sparse. PRMs from math reasoning score intermediate steps via Monte Carlo rollouts. Transferring PRM to KOSPI trading would score steps: market analysis → sector identification → risk assessment → position sizing.

## Hypothesis

A PRM trained on KOSPI trading reasoning traces will provide denser reward signals than outcome-only RL, leading to better Sharpe ratio and faster convergence.

## Approach sketch

Collect TradingAgents-style CoT traces on KOSPI historical data. Annotate step quality via Monte Carlo rollouts. Train PRM. Use for GRPO fine-tuning of Korean trading LLM.

## Novelty argument

Trade-R1 and GIFT already cover this conceptual space. KOSPI-specific Korean annotation is data collection, not a research contribution.

## Target venue

N/A — eliminated.

## Risks

Covered by existing papers.

## Pilot results

N/A — eliminated at Phase 3 first-pass filter.

## Lessons learned

(empty)

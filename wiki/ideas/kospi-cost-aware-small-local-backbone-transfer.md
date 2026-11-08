---
title: "Cost-Aware Small/Local Korean Backbone for Transferred LLM Trading Agents on KOSPI"
slug: kospi-cost-aware-small-local-backbone-transfer
status: failed
origin: "ideate: fix the 'cost-performance trade-off with smaller / locally hosted LLMs' open problem in the Korean setting — LoRA-fine-tune EXAONE/Qwen3-8B on the won 80k Korean-finance instruction set, drop into a transferred multi-agent pipeline, report Coordination Breakeven Spread vs GPT-4o-mini"
origin_gaps:
  - "[[llm-multi-agent-financial-trading]]"
  - "[[llm-finance]]"
tags:
  - kospi
  - cost-aware-evaluation
  - small-language-models
  - fine-tuning
  - market-transfer
target_venue: ""
novelty_score: ""
priority: 1
pilot_result: ""
failure_reason: "[filter] Closest prior work — Chinese Public REITs multi-agent LLM system (arXiv 2602.00082, Jan 2026) — already benchmarks a general-purpose LLM (DeepSeek-R1) against a fine-tuned Qwen3-8B inside a ported multi-agent trading framework and reports the fine-tuned small model matching or beating the large one. Swapping the market to KOSPI and the instruction data to won, plus adding the Coordination Breakeven Spread metric, is an incremental delta rather than a standalone contribution. The per-agent-role selective-fine-tuning sub-question is the only genuinely new angle and is better folded into a broader transfer study."
linked_experiments: []
date_proposed: 2026-08-31
date_resolved: 2026-08-31
---

## Motivation

The [[llm-multi-agent-financial-trading]] open problem "cost-performance trade-off with smaller or locally hosted LLMs" and the [[etf-asset-allocation-strategy-using-chatgpt]] question "can fine-tuning a smaller open-source LLM match GPT-4o-mini at lower cost?" both point at using a Korean-tuned small model inside a transferred agent pipeline. The won leaderboard (arXiv 2503.17963) released an 80k Korean-finance instruction dataset that makes such fine-tuning plausible.

## Hypothesis

A Qwen3-8B / EXAONE-7.8B model LoRA-fine-tuned on won's instruction set, placed in a transferred [[tradingagents-framework]] pipeline, achieves a positive Coordination Breakeven Spread on KOSPI (net of the 0.20% 2026 transaction tax) while a non-fine-tuned small model does not.

## Approach sketch

Fix the architecture ([[tradingagents-framework]]). Backbone ablation: GPT-4o-mini; Qwen3-8B raw; Qwen3-8B + won-LoRA; EXAONE-3.5 raw; EXAONE-3.5 + won-LoRA. Report CBS at KOSPI 2026 frictions and per-agent-role sensitivity to Korean fine-tuning (analyst vs trader vs risk).

## Novelty argument

Undercut by arXiv 2602.00082, which performs the general-vs-fine-tuned-small-model comparison in a ported multi-agent trading framework. The Korean instruction data and CBS metric do not lift this to a distinct contribution.

## Target venue

N/A — eliminated at Phase 3 first-pass filter.

## Risks

won instruction data is MCQA/QA-shaped and may not transfer to trading-decision behavior; heavy overlap with the "Architecture vs Backbone in Korea" candidate.

## Pilot results

N/A — eliminated at Phase 3 first-pass filter.

## Lessons learned

(empty)

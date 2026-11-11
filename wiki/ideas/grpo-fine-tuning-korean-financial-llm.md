---
title: "QuantAgent-RL: Online RL Adaptation for KOSPI Technical Analysis Signals"
slug: grpo-fine-tuning-korean-financial-llm
status: failed
origin: "ideate: Add online RL (DQN) to QuantAgent's multi-agent technical analysis pipeline for Korean-specific indicator learning"
origin_gaps:
  - "[[agentic-trading]]"
  - "[[llm-multi-agent-financial-trading]]"
tags:
  - rl
  - llm
  - kospi
  - technical-analysis
  - online-rl
target_venue: ""
novelty_score: ""
priority: 1
pilot_result: ""
failure_reason: "[filter] FLAG-TRADER (arxiv 2502.11433, ACL 2025 Findings) is essentially this idea: an LLM acts as the RL policy network, fine-tuned end-to-end with gradient-based RL from trading rewards (PEFT + policy gradient). Adding a DQN head on top of QuantAgent's signal pipeline is an incremental engineering extension of FLAG-TRADER, not a novel research contribution."
linked_experiments: []
date_proposed: 2026-07-21
date_resolved: 2026-07-21
---

## Motivation

QuantAgent ([[quantagent-multi-agent-trading-system]]) has no memory or learning between successive inference cycles. Korean markets have specific technical patterns (foreign investor reversal signals, earnings-driven momentum) that a learning system could exploit.

## Hypothesis

Adding online RL to adapt QuantAgent's indicator weighting using KOSPI-specific OHLCV data will improve directional accuracy on Korean equity markets.

## Approach sketch

Treat QuantAgent's 4-agent pipeline as a feature extractor. Add a DQN head with Korean-specific features (foreign investor net buy/sell, earnings calendar) as state. Train with transaction-cost-adjusted reward on KOSPI data.

## Novelty argument

FLAG-TRADER already covers RL fine-tuning of LLM trading agents at ACL 2025.

## Target venue

N/A — eliminated.

## Risks

Insufficient novelty vs. FLAG-TRADER.

## Pilot results

N/A — eliminated at Phase 3 first-pass filter.

## Lessons learned

(empty)

---
title: "KOSPI Regime-Aware Dynamic DAG-RL: RL Meta-Agent for Adaptive Orchestration Topology"
slug: kospi-regime-adaptive-dag-rl-trading
status: proposed
origin: "ideate: Breaking the shared 'static DAG' assumption of TradingAgents + DAG Orchestration — FINSABER (KDD 2025) shows LLMs fail regime transitions; an RL meta-agent dynamically selects orchestration topology per KOSPI regime"
origin_gaps:
  - "[[agentic-trading]]"
  - "[[llm-multi-agent-financial-trading]]"
tags:
  - rl
  - llm
  - kospi
  - multi-agent
  - dag-orchestration
  - regime-detection
  - meta-rl
target_venue: "NeurIPS 2026 / AAAI 2027"
novelty_score: ""
priority: 4
pilot_result: ""
failure_reason: ""
linked_experiments: []
date_proposed: 2026-07-21
date_resolved: ""
---

## Motivation

Both [[dag-based-agent-orchestration]] (FinAgent Orchestration) and [[tradingagents-framework]] share a critical assumption: the agent communication topology is fixed at system design time. FINSABER (arxiv 2505.07078, KDD 2025) shows empirically that LLM-based trading strategies are **overly conservative in bull markets and overly aggressive in bear markets** — a failure mode that stems from using the same static reasoning topology across different market regimes. The open problem in [[agentic-trading]] — "How to design adaptive DAG plans that respond to market regime shifts" — is unresolved in the literature.

KOSPI is especially sensitive to regime changes: foreign investor flows, the Samsung/SK Hynix semiconductor cycle, and Bank of Korea rate decisions create distinct bull/bear/sideways regime patterns where different information sources dominate.

## Hypothesis

An RL meta-agent that dynamically selects among 3 pre-designed orchestration DAG topologies (one per KOSPI regime) will reduce the regime-transition performance degradation observed in static-topology systems, achieving more consistent Sharpe ratio across bull/bear/sideways KOSPI conditions.

## Approach sketch

**Step 1 — Regime classifier**: Train a lightweight KOSPI regime detector (3-class: bull/bear/sideways) using features: KOSPI 200-day MA distance, ADX directional strength, foreign net buy/sell 20-day EMA, VKOSPI (Korea VIX). Rolling 60-day window.

**Step 2 — Pre-designed topology variants** using [[dag-based-agent-orchestration]]:
- **Bull topology**: Analyst-heavy (fundamentals + momentum); risk-manager is passive; debate rounds reduced to 1.
- **Bear topology**: Risk-manager-heavy (drawdown guard active); macro + sentiment agents weighted up; VIX-Korea observation mandatory.
- **Sideways topology**: Technical-analysis-heavy (QuantAgent-style pattern recognition); shorter holding periods; more frequent rebalancing.

**Step 3 — RL meta-agent**: Train a Contextual Bandit (or lightweight PPO) that observes the regime classifier probability vector and recent performance history (rolling 10-day Sharpe per topology), selects which topology to activate each trading day. Reward: next-day portfolio Sharpe contribution.

**Step 4 — Evaluation**: Backtest on KOSPI 7-stock universe (Samsung Electronics, SK Hynix, Hyundai Motor, POSCO, KB Financial, LG Chem, Kakao) over 2020–2024 walk-forward covering 4 distinct regime episodes.

## Novelty argument

The [[dag-based-agent-orchestration]] paper explicitly lists regime-adaptive DAG planning as an open problem. AlphaQuanter (arxiv 2510.14264, ACL 2026) introduces RL over single-agent tool workflows but not multi-agent topology selection. 3S-Trader (arxiv 2510.17393) does regime-adaptive scoring within a fixed pipeline. **This work is the first to frame regime adaptation as an RL meta-agent problem over multi-agent DAG topologies**, motivated by FINSABER's empirical failure analysis. KOSPI's regime dynamics make it the ideal evaluation setting.

## Target venue

NeurIPS 2026 or AAAI 2027 — the meta-RL framing fits top AI venues while the financial application and KOSPI-native dataset make it distinct from standard RL papers.

## Risks

**Feasibility: MEDIUM**

1. **Topology design requires domain expertise**: Pre-designing 3 meaningful DAG topologies requires knowing which KOSPI signals are informative per regime — needs validation with financial domain knowledge.
2. **Sparse regime episodes**: KOSPI bear episodes since 2018 (COVID crash, 2022 correction) provide only 2 clear bear windows — regime-specific RL may be data-starved for the bear topology.
3. **LLM API cost**: Running multiple topology configurations for online selection adds inference cost; the bandit must select before full execution to avoid cost multiplication.

## Pilot results

(Leave blank — filled in by /exp-pilot-eval in Phase 5.)

## Lessons learned

(empty — filled by /exp-eval after the idea reaches a terminal status)

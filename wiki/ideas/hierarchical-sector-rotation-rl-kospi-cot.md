---
title: "HiSeRA: Hierarchical Sector-Rotation RL Combining CoT ETF Framework and Timed Sub-Agents"
slug: hierarchical-sector-rotation-rl-kospi-cot
status: proposed
origin: "ideate: Combining the KOSPI-specific sector selection strength of CoT ETF framework with HARLF-style hierarchical RL for timing within selected sectors"
origin_gaps:
  - "[[agentic-trading]]"
  - "[[llm-finance]]"
tags:
  - rl
  - llm
  - kospi
  - hierarchical-rl
  - sector-rotation
  - multi-agent
  - korean-market
target_venue: "NeurIPS 2026 / ICAIF 2026"
novelty_score: ""
priority: 3
pilot_result: ""
failure_reason: ""
linked_experiments: []
date_proposed: 2026-07-21
date_resolved: ""
---

## Motivation

KOSPI has extreme sector concentration: semiconductors (Samsung Electronics, SK Hynix) + autos (Hyundai, Kia) + batteries (LG Energy, Samsung SDI) account for over 40% of index market cap. This creates a natural two-level decision problem: (1) which sectors to be in (high-level policy), and (2) when to enter and exit within each sector (low-level timing). The [[cot-based-llm-etf-allocation-framework]] excels at (1) — Korean news → KRX sector weights — but has no timing capability. HARLF (arxiv 2507.18560) shows that hierarchical RL (base agents → meta-agents → super-agent) improves portfolio return on US stocks, but uses generic news sentiment. Combining Korean-news-driven sector selection (high-level) with RL-timed entry/exit (low-level) within KOSPI's concentrated sectors is a new and domain-grounded contribution.

## Hypothesis

A two-level hierarchical system — CoT ETF framework as the high-level sector allocator + PPO-trained RL sub-agents for within-sector timing — will achieve higher Sharpe ratio on KOSPI than either the CoT ETF baseline alone or a flat RL baseline that optimizes both levels jointly.

## Approach sketch

**Level 1 (High-level sector selection)**: Run the existing [[cot-based-llm-etf-allocation-framework]] on Korean news to produce sector weights at weekly rebalancing frequency. This gives a sector allocation vector (e.g., 30% semiconductors, 20% auto, 10% energy-chemicals).

**Level 2 (Within-sector timing)**: For each of the 4–5 top-weighted sectors, train a separate PPO agent that observes OHLCV technical indicators for the KODEX sector ETF (RSI, MACD, Bollinger Bands, foreign investor net buy/sell, earnings calendar dummies). The agent learns a binary in/out timing signal at daily granularity. Reward: daily sector ETF return weighted by position size × Level-1 allocation weight.

**Level 3 (Meta-agent)**: A lightweight meta-agent (linear model or small MLP) learns to reweight Level-2 agents based on recent accuracy in each KOSPI regime (bull/bear/sideways). Trained via gradient-based optimization on 6-month rolling windows.

Evaluate on 2018–2024 KOSPI walk-forward backtest with 4 regime windows.

## Novelty argument

HARLF (arxiv 2507.18560) is the closest paper — it uses a 3-tier DRL architecture with lightweight LLM sentiment. HiSeRA differs on three key axes: (1) **Korean-native signals**: Korean news CoT framework for Level 1 vs. generic English sentiment; (2) **KOSPI sector structure**: the 11 KRX sector taxonomy is used as the natural hierarchy rather than individual stock portfolios; (3) **Earnings-calendar state augmentation**: Korean companies follow Q1/Q3 concentrated earnings seasons that create predictable sector dynamics not captured by price-only RL. No paper combines KOSPI sector structure + hierarchical RL + Korean language high-level policy.

## Target venue

ICAIF 2026 (ACM International Conference on AI in Finance) or NeurIPS 2026 Workshop on Sustainable Finance — strong fit for market-specific RL contributions with clear domain-grounded evaluation.

## Risks

**Feasibility: MEDIUM**

1. **Level interaction instability**: High-level allocation changes every week while low-level timing acts daily; the policy update frequency mismatch can cause training instability — need to fix high-level weights during low-level training.
2. **KODEX ETF data availability**: Need sector ETF daily OHLCV + foreign net buy/sell from Korea Exchange Open API (KRX). Public access exists but rate limits may constrain data collection speed.
3. **Regime labeling subjectivity**: Bull/bear/sideways regime labels for KOSPI are typically defined by 200-day MA crossovers; the meta-agent's effectiveness depends on regime label quality and stability.

## Pilot results

(Leave blank — filled in by /exp-pilot-eval in Phase 5.)

## Lessons learned

(empty — filled by /exp-eval after the idea reaches a terminal status)

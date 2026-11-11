---
title: "KOSPI CoT-RL: GRPO Feedback Loop for Korean ETF Allocation"
slug: kospi-cot-rl-grpo
status: proposed
origin: "ideate: CoT ETF allocation framework (etf-paper) has no learning mechanism and was only tested in H1 2024 bull market — adding GRPO policy optimization creates a self-improving Korean ETF allocator"
origin_gaps:
  - "[[llm-finance]]"
  - "[[agentic-trading]]"
tags:
  - rl
  - llm
  - kospi
  - etf
  - grpo
  - korean-market
  - chain-of-thought
target_venue: "ICLR 2027 / EMNLP 2026"
novelty_score: ""
priority: 4
pilot_result: ""
failure_reason: ""
linked_experiments: []
date_proposed: 2026-07-21
date_resolved: ""
---

## Motivation

The [[cot-based-llm-etf-allocation-framework]] demonstrated that a two-stage CoT pipeline using Korean financial news can outperform KOSPI 200 and domestic AI-managed ETFs in a 6-month bull market (H1 2024). However, this framework has a critical limitation: **no feedback loop**. The LLM's allocation policy is fixed at inference time, receives no gradient signal from realized portfolio returns, and has never been tested in bear or sideways KOSPI conditions. The gap in [[llm-finance]] — "Does the framework hold in bear/sideways regimes?" — directly motivates this work.

Recent RL-for-LLM results (FLAG-TRADER, Trading-R1) demonstrate that GRPO (Group Relative Policy Optimization, the same algorithm behind DeepSeek-R1) can fine-tune LLMs with trading returns as the reward signal. No paper has applied this to a Korean-market-specific CoT ETF pipeline.

## Hypothesis

Adding a GRPO reinforcement learning feedback loop to the CoT-based KOSPI ETF allocation framework will produce a self-improving allocation policy that maintains or improves Sharpe ratio in bear and sideways KOSPI conditions compared to the zero-shot CoT baseline.

## Approach sketch

Start from the existing two-stage CoT pipeline ([[cot-based-llm-etf-allocation-framework]]): Korean news headlines → Task1 keyword extraction → Task2 sector ETF weights. Instead of using GPT-4o-mini's fixed zero-shot weights, wrap the LLM policy in a GRPO training loop: sample K independent allocation outputs for each news batch (forming a group), compute realized ETF portfolio returns over the next rebalancing window as the reward, and update the LLM's parameters using the relative advantage within the group (as in DeepSeek-R1's GRPO). Use LoRA/PEFT on an open-source Korean bilingual LLM (EXAONE-3.5 or HyperCLOVA-X) to keep GPU cost low. Evaluate on a 2018–2024 KOSPI walk-forward backtest covering COVID crash (bear), 2021 semiconductor boom (bull), and 2022 rate-hike correction (sideways) regimes.

## Novelty argument

The closest published work is FLAG-TRADER (arxiv 2502.11433, ACL 2025) and Trading-R1 (arxiv 2509.11420), but both operate on US stocks with English signals. News-Aware Direct RL (arxiv 2510.19173) tests on KS11 KOSPI index but uses only English-language sentiment as RL observation — it does not leverage the structured Korean-news CoT framework or KODEX sector ETFs. **The specific contribution is GRPO fine-tuning applied to the existing Korean CoT ETF architecture using KRX sector ETF returns as reward**, enabling Korean language financial reasoning that improves over rolling KOSPI regimes. No existing paper does this combination.

## Target venue

EMNLP 2026 (FinNLP workshop) or ICLR 2027 — the KOSPI-native evaluation dataset and Korean-language signal integration are novel contributions that would be well-received in NLP × finance venues.

## Risks

**Feasibility: HIGH**

1. **Reward sparsity**: Monthly ETF rebalancing gives only ~12 reward signals per year; may need daily or weekly reward proxy (e.g., next-day ETF price change weighted by allocation) to provide dense enough gradient signal for GRPO.
2. **Lookahead bias in news alignment**: News publication time vs. market price timestamp alignment must be verified carefully — the CoT ETF paper does not model transaction costs or lookahead bias rigorously.
3. **Korean LLM fine-tuning cost**: PEFT (LoRA) on EXAONE-3.5-7.8B should be manageable on 1–2 A100 GPUs; full fine-tuning is out of scope.

## Pilot results

(Leave blank — filled in by /exp-pilot-eval in Phase 5.)

## Lessons learned

(empty — filled by /exp-eval after the idea reaches a terminal status)

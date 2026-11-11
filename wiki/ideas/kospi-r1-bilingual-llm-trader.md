---
title: "KOSPI-R1: Korean-Native Bilingual RL Trading LLM"
slug: kospi-r1-bilingual-llm-trader
status: failed
origin: "ideate: Apply Trading-R1 style curriculum RL to a Korean bilingual LLM using Korean + English news as dual-language observations for KOSPI trading"
origin_gaps:
  - "[[llm-finance]]"
  - "[[agentic-trading]]"
tags:
  - rl
  - llm
  - kospi
  - korean-language
  - bilingual
  - fine-tuning
target_venue: ""
novelty_score: ""
priority: 1
pilot_result: ""
failure_reason: "[filter] Trading-R1 (arxiv 2509.11420) already implements curriculum SFT+RL with volatility-adjusted reward for LLM trading, and FinRL-DeepSeek (arxiv 2502.07393) covers LLM-infused CVaR-PPO. A Korean bilingual extension adds engineering work but no conceptual novelty; the Korean language signal advantage is an incremental contribution insufficient for a standalone venue-worthy paper without a Korean-language financial NLP benchmark, which is a separate multi-year project."
linked_experiments: []
date_proposed: 2026-07-21
date_resolved: 2026-07-21
---

## Motivation

All existing RL fine-tuned LLM trading systems (FLAG-TRADER, Trading-R1, FinRL-DeepSeek) operate exclusively on English financial signals. Korean news contains market-moving KOSPI information that may arrive earlier in Korean than in English translation. A Korean bilingual LLM fine-tuned with RL rewards from KOSPI returns might exploit this information advantage.

## Hypothesis

A GRPO-fine-tuned Korean bilingual LLM ingesting Korean + English news jointly will achieve higher Sharpe ratio on KOSPI than English-only RL trading systems.

## Approach sketch

Fine-tune EXAONE-3.5-7.8B with curriculum RL (SFT cold-start → GRPO), mirroring Trading-R1's three-stage approach. Training corpus: Korean Naver Finance news + English Reuters/Bloomberg for KOSPI-listed companies, 2018–2024. Reward: next-week KOSPI sector ETF portfolio return.

## Novelty argument

The Korean bilingual signal is the sole differentiator from Trading-R1. Without a public Korean financial NLP benchmark, the contribution reduces to an engineering paper.

## Target venue

N/A — eliminated at Phase 3 first-pass filter.

## Risks

Insufficient novelty for a top-venue submission; Korean-language advantage cannot be independently measured without a Korean financial benchmark.

## Pilot results

N/A — eliminated at Phase 3 first-pass filter.

## Lessons learned

(empty)

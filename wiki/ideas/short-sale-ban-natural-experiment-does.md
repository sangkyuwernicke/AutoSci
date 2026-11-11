---
title: "Short-Sale Ban Natural Experiment: Does the Bear Debater Matter for Long-Only KOSPI Multi-Agent Trading"
slug: short-sale-ban-natural-experiment-does
status: proposed
origin: "ideate: user-directed direction — validate the 'multi-agent performs well' claim on KOSPI and anticipate problems that only surface there. Korea fully banned short selling 2023-11-05 → 2025-03-31 (~17 months), so the 2024-01 → 2026-08 evaluation window straddles a regime in which the bear side of a bull/bear debate had no direct tradable expression. Grounded in [[tradingagents-framework]] (symmetric bull/bear researchers, BUY/SELL/HOLD) and the 2026 finding that debate raises raw returns in bull markets but amplifies losses in adverse ones."
origin_gaps: ["[[llm-multi-agent-financial-trading]]", "[[agentic-trading]]", "[[agent-communication]]"]
tags: [kospi, multi-agent-debate, short-selling-ban, ablation-study, market-microstructure, korean-market]
target_venue: ICAIF 2026 / NeurIPS 2026 Workshop on Generative AI in Finance
novelty_score: 2
priority: 3
pilot_result: ""
failure_reason: ""
linked_experiments: []
date_proposed: 2026-10-05
date_resolved: ""
---

## Motivation

US-built multi-agent trading frameworks assume a symmetric action space. [[tradingagents-framework]] stages a bull-vs-bear researcher debate before the trader acts, and [[tradingagents-multi-agents-llm-financial-trading]] credits that debate for part of its gain. On KOSPI the assumption broke for ~17 months: short selling was fully banned from 2023-11-05 until 2025-03-31 and resumed afterwards. Under a long-only action space the bear researcher can only argue for "hold" or "sell what you own". It has no way to express a bearish view as a position. Nobody has isolated whether the bear role is doing real work in that setting or is decorative.

[[when-agents-trade-live-multi-market]] finds architecture, not backbone, drives live performance, and the wiki's gap list repeatedly asks which agent components actually contribute ("what is the marginal contribution of each agent pool", "how much comes from debate vs memory vs character"). The ban gives an externally imposed, dated constraint that makes the bear role's marginal value measurable, which is rarely available in agent ablations.

## Hypothesis

**H1 (role vacuity):** Under a long-only action space, removing the bear researcher changes Sharpe by less than a pre-registered margin, while under an action space with a direct bearish expression (inverse ETF or short) removing it costs significantly more. The bear role's value depends on whether its output is actionable.

**H2 (information content):** The bear researcher's score has lower predictive content for next-5-day returns during the ban window than after it, because the ban suppressed downside price discovery.

**H3 (fix):** Reframing the bear role as an "exit-timing / hedge-sizing" agent whose output maps to position reduction or inverse-ETF exposure recovers the value lost under long-only.

## Approach sketch

Base framework is [[tradingagents-framework]] on 15 KOSPI large caps plus KODEX 200, 2024-01 → 2026-08, with a 2023-H2 warm-up. Single backbone, 3 seeds. The core design is 3 bear conditions × 2 action spaces = 6 cells.

- Bear condition: B1 full bear researcher (baseline); B0 bear researcher removed (bull-only analysis plus trader); BX bear reframed as exit-timing/hedge-sizing.
- Action space: A_long (BUY/HOLD/SELL-own only); A_hedge (A_long plus KOSPI inverse ETF, available even during the ban).
- A short-allowed counterfactual cell is an optional extension, valid only post-ban.
- Results are reported by sub-window: ban (2024-01 → 2025-03-30) vs post-ban, plus the 2026-07 crash as a stress sub-window.
- Standard metrics only: Sharpe, Sortino, MDD, CVaR, cumulative return. Diagnostics: bear decision-flip rate (how often the bear changes the trader's final call) and IC of bear score vs forward returns.
- Backtest realism follows [[stocksim-framework]]-style discipline: 0.20% transaction tax, slippage, ±30% price limits, strict timestamp guard.

## Novelty argument

Existing ablations remove roles on a single symmetric-action market (crypto, US equities, Japanese equities). None exploits a regulatory action-space asymmetry as a natural experiment, and none asks whether a debate role is actionable rather than merely informative. Closest prior work found in the quick screen — AMA (2510.11695), the crypto three-agent ablation (2501.00826), and the TradingAgents ablations — do not vary the action space or condition on a short-sale regime. The contribution is a causal-ish handle on "does debate role X matter" via an externally imposed constraint, plus a Korea-specific bearish expression (inverse ETFs) as the remedy.

## Target venue

ICAIF 2026 (market-specific evaluation) as primary; NeurIPS 2026 Generative-AI-in-Finance workshop as fallback.

## Risks

Feasibility: medium-high. The 6-cell design is cheap.

1. Single base framework (TradingAgents): a null result may be framework-specific. State as a limitation.
2. The ban window overlaps the 2024 bull run, so ban vs post-ban is confounded with market regime. Mitigate by toggling the action space inside both windows (it is a design variable, not just a calendar variable) and reporting H2 as correlational.
3. LLM leakage on 2024 KOSPI moves cannot be fully removed with a closed backbone. Report the 2026-07 crash separately.
4. Inverse-ETF liquidity and tracking error must be modeled, or A_hedge flatters the result.
5. Overlaps in spirit with [[kospi-information-diet-vs-reasoning-scaffold]] (same base framework). Keep the two papers separable: this one varies roles/actionability, that one varies input channels.

## Pilot results

(Leave blank — filled in by /exp-pilot-eval in Phase 5.)

## Lessons learned

(empty — filled by /exp-eval after the idea reaches a terminal status)

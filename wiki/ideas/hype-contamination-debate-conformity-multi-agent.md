---
title: "Walking Into the Warning List: Regulator-Labeled Retail Hype and Provenance-Typed Debate for Multi-Agent LLM Traders on KOSPI/KOSDAQ"
slug: hype-contamination-debate-conformity-multi-agent
status: proposed
origin: "ideate: user-directed direction — anticipate KOSPI/KOSDAQ-specific failure modes of multi-agent LLM trading. v2 (2026-10-05, user chose this idea to develop): replaces the self-defined hype label with Korea Exchange (KRX) market-alert designations and inquiry disclosures as external ground truth, makes the hypothesis two-sided after Homo Silicus (SSRN 5901742) reported LLM agents retreat from viral signals, and replaces the generic source-credibility gate with a provenance-typed debate. Grounded in SoK (arXiv 2609.19705, universal information-source weakness) and [[agentverse-facilitating-multi-agent-collaboration-exploring]] (conformity)."
origin_gaps: ["[[llm-multi-agent-financial-trading]]", "[[agent-communication]]", "[[agentic-trading]]"]
tags: [kospi, kosdaq, retail-hype, krx-market-alert, conformity, provenance-typed-debate, multi-agent-debate, ablation-study, korean-market]
target_venue: ICAIF 2026 / EMNLP 2026 (FinNLP)
novelty_score: 2
priority: 3
pilot_result: ""
failure_reason: ""
linked_experiments: []
date_proposed: 2026-10-05
date_resolved: ""
---

## Motivation

Multi-agent trading frameworks feed a sentiment analyst's output into a bull/bear debate ([[tradingagents-framework]]). That design was tuned on US text. In Korea, a visible share of short-horizon price action in small and mid caps is retail-driven: price and volume surge on narrative with no material disclosure behind it. The exchange itself polices this. KRX runs a three-tier market-alert system (investment caution → warning → risk) with mechanical triggers such as a 60% five-day surge, and it issues inquiry disclosures (조회공시) when a price move has no public explanation. Those designations are official, timestamped, and exogenous to any researcher's judgment. Press analysis in 2026 reports that about one in four warned stocks falls 30% within a month, and the inquiry-disclosure literature finds retail investors net-buying through the event while institutions sell.

Two things are unknown for LLM agent teams. First, what do they do while a stock is surging toward a designation: chase it, or abstain? Homo Silicus (SSRN 5901742) finds LLM agents *reduce* buying under viral attention shocks, but in an environment where costs were explicit and calculable. A real market gives no such cost sheet, so the direction is open. Second, does the debate scaffold change that behavior? Stance-typed debate (one agent assigned bull, one bear) gives the bear no privileged access to verifiable evidence, so it can concede to a persuasive narrative (conformity, cf. [[agentverse-facilitating-multi-agent-collaboration-exploring]]; sycophantic convergence is documented for trading debate in arXiv 2609.29701).

## Hypothesis

**H1 (participation, two-sided, pre-registered):** On episodes later designated by KRX, an LLM trading agent's long exposure at the pre-designation surge differs from its exposure on matched non-designated surges. We do not fix the sign. Late participation and abstention are both reportable results. Abstention carries a measurable "cost of prudence" on surges that continue.

**H2 (debate effect):** Moving from a single agent to stance-typed debate changes participation toward the retail-flow direction, measured by the bear researcher's concession rate without new verifiable evidence.

**H3 (provenance-typed debate):** Assigning debate roles by evidence provenance, not by stance, and permitting a stance change only on new verifiable evidence, improves a Hype Discrimination Score (separating reverting designated episodes from continuing non-designated surges) without a significant loss on non-event days.

**H4 (regulator visibility):** Making KRX alerts and inquiry disclosures visible in the input helps less than H3's structural fix, because the notice often arrives after most of the surge.

## Approach sketch

**Labels (external, not researcher-defined).** KRX market-alert designations and inquiry disclosures, 2024-01 → 2026-08, taken from the exchange's public data. Event time is the designation date; the agent's decision is evaluated at t−k days (k pre-registered) when the stock is already surging. Matched controls are non-designated surges of similar magnitude, sector, and size, using the mechanical thresholds so that near-threshold non-designated stocks are a natural comparison. A shuffled-designation-date placebo checks for label leakage. The labeling regime changed during the window (SK hynix warning in 2025-12, then top-100 market-cap exemption from 2026-05), so regime is a covariate and exempted names are excluded from post-change labels.

**Debate structures (3):** single agent; stance-typed bull/bear ([[tradingagents-framework]]); provenance-typed (PTD). In PTD, a *narrative* agent may cite any text but every claim is tagged by source type; a *verifier* agent is restricted to timestamped verifiable evidence (DART disclosures, investor net-flow, KRX notices, price/volume). Stance emerges from the evidence, and the trader accepts a stance flip only when new verifiable evidence is cited.

**Input arms (2):** with/without the narrative channel (news and sentiment). A third optional arm adds KRX notice visibility for H4.

**Core grid:** 3 debate structures × 2 input arms = 6 cells, 3 seeds, one backbone, evaluated on three strata: designated episodes, matched non-designated surges, non-event days.

**Metrics:** Hype Participation Rate (long at t−k on designated episodes), post-designation 5/10/20-day return of held positions, late-entry rate, cost of prudence (forgone return on continuing non-designated surges), Hype Discrimination Score, bear concession rate without new verifiable evidence, plus standard Sharpe/MDD on the non-event stratum. Backtest realism: 0.20% transaction tax, slippage, ±30% price limits, margin and trading restrictions after designation, strict timestamp guard.

## Novelty argument

Closest prior work and where this differs:

- **Adversarial contagion** (Contagion on the Trading Floor 2609.19789, Poisoning Agentic Alpha 2608.24069, TradeTrap 2512.02261, AutoRedTrader 2605.09185): all inject attacker-crafted signals. This studies the market's own endogenous hype, labeled by the regulator.
- **Homo Silicus (SSRN 5901742):** LLM agents retreat from viral signals under explicit costs, in a stylized environment. This tests the same question on real labeled episodes and in a multi-agent scaffold, with the sign left open.
- **FraudDebate-Agent and Disagree-or-Commit (FinCom 2606.00939):** evidence-modality roles exist for fraud detection, and a commit rule exists for finance debate. Provenance-typed roles with a verifiable-evidence flip rule, applied to trading hype, are new as far as the screen found, but are an incremental design move rather than a new paradigm.
- **Contribution that carries the paper:** a regulator-labeled hype benchmark for LLM trading agents (no prior work found using KRX designations as labels) plus a debate-structure ablation on it. The honest expectation is a modest novelty score; the benchmark and the two-sided result are the defensible parts.

## Target venue

ICAIF 2026 primary. EMNLP 2026 FinNLP if the Korean-language channel result carries it. A benchmark/dataset track is a plausible fit for the labeled-episode set.

## Risks

Feasibility: medium.

1. **Data access.** KRX alert history is public but the exact download route and licence must be confirmed before the pilot. Korean news text around events (the narrative channel) remains the hard dependency: BigKinds, AI-Hub, or a licensed source. Without it the narrative arm degrades to headline-only.
2. **Label regime change.** Criteria were revised after the SK hynix designation and top-100 names were exempted from 2026-05; late-window labels are not comparable to early ones. Model it explicitly or truncate.
3. **Label validity (surfaced by cross-model review).** KRX triggers are mechanical functions of price and volume, so a designation marks "extreme surge", not necessarily "narrative hype", and post-designation decline can be plain mean reversion. A model that sees the surge can anticipate the designation without any hype reasoning. Mitigations: compare against near-threshold non-designated surges (same surge size, no designation), add the inquiry-disclosure subset (no public explanation for the move) as a second label family, and report results separately for each. Do not claim the label proves narrative contamination.
4. **Sample size.** Designated episodes may be few per quarter; matched-control design needs enough near-threshold pairs. Count them before committing.
5. **Two-sided result risk.** If agents simply abstain everywhere, H2/H3 have little to act on. The cost-of-prudence metric keeps that outcome publishable, but it shifts the paper from "failure mode" to "overcaution".
6. **LLM leakage** on known 2024–2025 episodes; report the post-2026 window separately and use the placebo.
7. **Overlap with [[kospi-information-diet-vs-reasoning-scaffold]]:** that idea values input channels and scaffold depth in aggregate; this one studies a labeled failure episode and a role-typing mechanism. KRX alerts are not in its D5 bundle.

## Pilot results

(Leave blank — filled in by /exp-pilot-eval in Phase 5.)

## Lessons learned

(empty — filled by /exp-eval after the idea reaches a terminal status)

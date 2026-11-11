---
title: "Effective Agent Count on a Concentrated Index: Heterogeneous-Backbone vs Persona Debate for KOSPI Multi-Agent Trading"
slug: effective-agent-count-concentrated-index-heterogeneous
status: proposed
origin: "ideate: user-directed direction — anticipate problems that emerge when multi-agent trading is validated on KOSPI. Index returns are dominated by two names (Samsung Electronics, SK Hynix), and 2026 debate literature finds same-backbone debate often no better than majority vote (arXiv 2605.00914, 2601.19921) while heterogeneous model families reduce correlated errors. Related to [[tradinggpt-multi-agent-system-layered-memory]] (persona/character diversity never ablated against debate)."
origin_gaps: ["[[llm-multi-agent-financial-trading]]", "[[multi-agent-collaboration-network]]", "[[agent-communication]]"]
tags: [kospi, multi-agent-debate, agent-diversity, effective-sample-size, concentration, ablation-study, korean-market]
target_venue: ICAIF 2026 / NeurIPS 2026 Workshop on Generative AI in Finance
novelty_score: 2
priority: 2
pilot_result: ""
failure_reason: ""
linked_experiments: []
date_proposed: 2026-10-05
date_resolved: ""
---

## Motivation

Multi-agent trading systems claim gains from having several specialist or persona agents deliberate ([[tradingagents-framework]], [[tradinggpt-framework]]). Most use one backbone with different role or persona prompts. If those agents share the same knowledge gaps and biases, their decisions are strongly correlated and the "team" behaves like one agent with extra cost. KOSPI sharpens this: index-level outcomes hinge on a few flow-driven mega-caps, so correlated agent errors on those names are expensive and cannot be diversified away across a 15-name universe. [[tradinggpt-multi-agent-system-layered-memory]] explicitly leaves the persona-vs-memory-vs-debate attribution unablated, and [[when-agents-trade-live-multi-market]] finds architecture dominates backbone without asking how much independent information the architecture actually aggregates.

## Hypothesis

**H1 (redundancy):** In a same-backbone persona team on KOSPI, the effective number of independent agents, N_eff computed from the eigenvalue spectrum of the agents' decision-correlation matrix, is close to 1, and debate adds no Sharpe over simple majority vote.

**H2 (concentration):** N_eff is lowest, and debate's advantage over majority vote smallest, on index-dominant names (Samsung Electronics, SK Hynix) relative to other large caps.

**H3 (heterogeneity):** A team mixing model families raises N_eff and recovers a debate advantage over majority vote that the homogeneous team lacks.

## Approach sketch

Base framework [[tradingagents-framework]] on 15 KOSPI large caps plus KODEX 200, 2024-01 → 2026-08. Team conditions: homogeneous (one backbone, persona prompts), heterogeneous (a closed API model, an open Qwen-family model, and a Korean-trained open model run locally). Aggregation conditions: debate, majority vote, best-single-agent. That gives a 2×3 grid at fixed agent count (3 specialists), 3 seeds.

Measured per cell: Sharpe, Sortino, MDD, CVaR; N_eff from per-decision agent correlation; fraction of debates whose final call differs from the majority vote. Split results by index-dominant vs other names and by market sub-window. Cost per decision is reported alongside, since heterogeneous teams are more expensive to run.

## Novelty argument

The "same-backbone debate ≈ majority vote" and "diversity should come from model families" results are established for reasoning benchmarks (2605.00914, 2601.19921, 2606.19826). The finance-specific delta is measuring effective independent information in a trading team, tying redundancy to index concentration, and testing whether a Korean-native model adds distinct signal on Korean inputs. That delta is real but modest, and the idea sits close to the failed [[kospi-cost-aware-small-local-backbone-transfer]], which swapped a backbone rather than mixing families. Treat as a lower-priority, supporting study.

## Target venue

ICAIF 2026 or a NeurIPS 2026 finance workshop.

## Risks

Feasibility: medium.

1. Novelty is the main risk; reviewers may read it as a financial rerun of general debate-diversity results.
2. Running a Korean-trained open model locally adds infrastructure cost. A smaller second open family is an acceptable fallback.
3. Heterogeneous teams confound diversity with raw capability differences. Include a best-single-agent arm to separate them.
4. N_eff on three-way discrete decisions is coarse; consider a soft-score variant.

## Pilot results

(Leave blank — filled in by /exp-pilot-eval in Phase 5.)

## Lessons learned

(empty — filled by /exp-eval after the idea reaches a terminal status)

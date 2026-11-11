---
title: "LLM-Verbalized vs Raw Dynamic Lead-Lag Signals: Does Cross-Market Reasoning Add Value Over the Number?"
slug: llm-verbalized-vs-raw-dynamic-lead
status: proposed
origin: "ideate: user-directed direction — what is the effect of adding an agent that analyzes correlation with foreign indices like NASDAQ for KOSPI? Companion to [[global-linkage-channel-ablation-blanket-index]], which fixes the channel formulation (correlation/beta) and asks whether the channel helps; this idea instead fixes a dynamic cross-market signal and asks whether the AGENT needs to reason in natural language about it, or whether the raw number is enough."
origin_gaps:
  - "[[llm-multi-agent-financial-trading]]"
  - "[[agentic-trading]]"
tags:
  - kospi
  - ablation-study
  - cross-market-correlation
  - lead-lag
  - agent-orchestration
  - llm-reasoning
  - korean-market
target_venue: "NeurIPS 2026 Workshop on Generative AI in Finance / ICAIF 2026"
novelty_score: 4
priority: 5
pilot_result: ""
failure_reason: ""
linked_experiments: []
date_proposed: 2026-09-21
date_resolved: ""
---

## Motivation

DeltaLag (arXiv 2511.00390) shows that *dynamic*, pair-specific lead-lag structure between assets — discovered end-to-end rather than assumed fixed — substantially outperforms fixed-lag and statistical baselines for portfolio construction, but it is a pure deep-learning system with no LLM-agent layer and no cross-country application. Meanwhile, the LLM multi-agent trading literature ([[tradingagents-framework]] and peers) routinely feeds quantitative features (technical indicators, sentiment scores) into agent contexts, and the field has generally assumed that wrapping numeric signals in natural-language "reasoning" (a dedicated analyst agent that discusses a number rather than the trader simply reading it) improves decision quality — but no paper has isolated this assumption as its own controlled ablation axis. This matters specifically for the KOSPI global-linkage question: if a future system computes *which* US name currently leads a given KOSPI stock and by how much (a genuinely dynamic, time-varying relationship — Samsung's lead-lag partner and lag length plausibly shift as the AI-capex narrative evolves), does routing that number through an LLM specialist agent before the trader sees it change the trading outcome, or does it only add latency, cost, and hallucination risk?

## Hypothesis

**H1:** A dynamic (time-varying, pair-specific) lead-lag signal between KOSPI names and their US mega-cap tech/semis counterparts has positive marginal decision value over a no-signal baseline.

**H2 (the core question):** Passing the same numeric lead-lag signal through a dedicated LLM specialist agent that verbalizes/reasons about it before the trader agent sees it does **not** reliably outperform injecting the raw number directly into the trader's context — i.e., the natural-language "reasoning" step adds cost and latency without a matching gain in risk-adjusted performance, and may introduce hallucination (misstating the signal's direction, lag, or strength).

## Approach sketch

**Signal construction (revised per cross-model review to reduce feasibility risk):** rather than training a full DeltaLag-style cross-attention model from scratch (flagged by Review LLM as a nontrivial ML engineering sub-project with real risk of non-convergence), the primary pilot uses a much simpler, well-understood dynamic-lead-lag proxy: a rolling cross-correlation-with-optimal-lag search — for each KOSPI name, search lags 0-3 trading days against a small candidate basket of US leaders (e.g. NVIDIA, SOX index, Nasdaq-100) over a rolling 60-day window, and take the lag/partner with maximum absolute correlation as the "current leader" signal, updated daily. This preserves the "dynamic, pair-specific, not fixed" property that DeltaLag's ablations show matters, at a fraction of the engineering cost. A DeltaLag-style trained cross-attention model remains an optional stretch upgrade (Approach v2) only if the simple version shows a clear enough effect to justify the added infrastructure.

**Three-condition ablation** inside the [[kospi-information-diet-vs-reasoning-scaffold]] harness (same backbone, universe, period, execution engine as the sibling ideas):
- **(a) No signal** — baseline, no lead-lag information.
- **(b) Raw signal** — the leading name, lag, and correlation strength injected directly as structured text/numbers into the trader agent's context.
- **(c) LLM-verbalized signal** — the identical numbers first passed through one frozen-backbone specialist agent that produces a short natural-language rationale (e.g., "SK Hynix has tracked NVIDIA with a 1-day lag and 0.6 correlation over the past 60 days; NVIDIA fell 3% yesterday, suggesting downside pressure today") before the trader sees it.

**Metrics:** Sharpe, cumulative return, MDD (decision quality); decision latency and token/cost overhead of (c) vs (b); a hallucination/faithfulness check — an automated pass comparing each verbalization in (c) against the underlying numeric signal it was given, flagging any case where direction, lag, or strength is misstated.

**Controls:** identical backbone and prompt skeleton across (a)/(b)/(c) except for the lead-lag content itself; placebo shuffled lead-lag signal (expect (b) and (c)'s advantage over (a) to vanish); the simple lag-search signal is validated against basic sanity checks (e.g., does the selected "leader" change plausibly around known events) before being used in the trading ablation.

## Novelty argument

No prior paper isolates "LLM-verbalization of a learned/computed quantitative signal" as its own standalone ablation axis inside a multi-agent trading pipeline — existing frameworks either feed numbers directly (most technical-indicator-based systems) or always route everything through analyst agents (debate-based systems like [[tradingagents-framework]]), without a controlled head-to-head of the same information through both paths. DeltaLag establishes that dynamic lead-lag signals have value but has no LLM-agent layer at all. This idea's contribution is orthogonal to and broader than the specific KOSPI-NASDAQ question in [[global-linkage-channel-ablation-blanket-index]]: it uses the cross-market lead-lag setting as a concrete, motivated testbed for a general open question in LLM multi-agent system design — [[llm-multi-agent-financial-trading]]'s gap on "optimal agent orchestration strategies for task-agent assignment" and [[agentic-trading]]'s gap on "optimal communication structure for different task categories" both bear directly on whether verbalization is a first-class design choice or an unexamined default.

Cross-model review (Review LLM, standard/method focus) scored 7/10, verdict "needs-work," with the primary actionable concern being the feasibility risk of training a DeltaLag-style model from scratch — the reviewer explicitly recommended substituting a simpler rolling cross-correlation-with-optimal-lag search while preserving the core (b)-vs-(c) ablation question, which has been incorporated directly into the Approach sketch above (the DeltaLag-style trained model is now an optional v2 stretch goal, not a prerequisite).

## Target venue

NeurIPS 2026 Workshop on Generative AI in Finance — best fit for the general LLM-agent-design contribution (verbalization vs. raw-signal value). ICAIF 2026 as a fallback if the KOSPI-specific cross-market framing carries more weight than the general methodological question.

## Risks

**Feasibility: MEDIUM** (reduced from the original DeltaLag-based design per review).

1. **Signal quality of the simplified lag-search proxy.** A 0-3-day rolling correlation search over a small US candidate basket is much cruder than DeltaLag's learned attention mechanism and may not find a genuine, stable enough lead-lag relationship to produce a meaningful (b) vs. (a) gap in the first place — if H1 itself fails, H2 (the core reasoning-vs-raw question) cannot be cleanly tested. Mitigation: validate the signal's standalone predictive power (e.g., simple regression of next-day KOSPI-name return on the lagged leader return) before running the full agent ablation.
2. **Hallucination-check automation.** Detecting whether an LLM verbalization "misstates" a numeric signal requires a reliable automated comparator (e.g., a smaller model or rule-based parser extracting the claimed direction/lag/strength from the LLM's text); building this checker is itself a small sub-project with its own failure modes (false positives/negatives).
3. **Overlap risk with [[global-linkage-channel-ablation-blanket-index]]** if not kept distinct: that idea's D6a/D6b raw-vs-agent sub-ablation already tests something similar for the *correlation/beta* channel specifically. This idea's contribution must be framed as the general reasoning-vs-raw question using a *different, dynamic* signal (lead-lag, not correlation) as its testbed, and ideally analyzed jointly with the sibling idea's D6 raw-vs-agent results as a two-signal replication of the same underlying question, strengthening both rather than duplicating either.
4. **Latency/cost overhead of condition (c)** may make it commercially uninteresting regardless of the performance result — this is itself part of the finding (Actionable Items should report the overhead explicitly, not just performance deltas).

## Pilot results

(Leave blank — filled in by /exp-pilot-eval in Phase 5.)

## Lessons learned

(empty — filled by /exp-eval after the idea reaches a terminal status)

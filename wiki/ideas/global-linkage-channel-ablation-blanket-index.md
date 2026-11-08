---
title: "Global-Linkage Channel Ablation: Blanket Index Correlation vs Concentration-Weighted AI-Capex Exposure for KOSPI LLM Trading Agents"
slug: global-linkage-channel-ablation-blanket-index
status: proposed
origin: "ideate: user-directed direction — what is the effect of adding an agent that analyzes correlation with foreign indices like NASDAQ for KOSPI? Grounded in the sibling [[kospi-information-diet-vs-reasoning-scaffold]] ablation (whose D0-D5 channels are all domestic and omit any global/foreign-market signal) and the empirically documented 2026 KOSPI-NASDAQ correlation regime shift."
origin_gaps:
  - "[[agentic-trading]]"
  - "[[llm-multi-agent-financial-trading]]"
  - "[[llm-finance]]"
tags:
  - kospi
  - ablation-study
  - information-channels
  - cross-market-correlation
  - regime-dependence
  - korean-market
  - evaluation-methodology
target_venue: "ICAIF 2026 / EMNLP 2026 (FinNLP) / NeurIPS 2026 Workshop on Generative AI in Finance"
novelty_score: 4
priority: 5
pilot_result: ""
failure_reason: ""
linked_experiments: [global-linkage-channel-ablation-blanket-index]
date_proposed: 2026-09-21
date_resolved: ""
---

## Motivation

The sibling wiki idea [[kospi-information-diet-vs-reasoning-scaffold]] ablates five KOSPI information channels (D0 price/technical, D1 English news, D2 Korean news, D3 DART disclosures, D4 investor net-flow, D5 combined) crossed against decision-orchestration complexity — but every one of those channels is **domestic**. None represents foreign/global market information at all, despite the fact that KOSPI's relationship to global markets has structurally changed: the 60-day rolling correlation between KOSPI and NASDAQ-100 reached roughly 0.50 in mid-to-late 2026, close to a 5-year high and nearly three times the 5-year average of ~0.16, driven by Samsung Electronics and SK Hynix — which together account for more than half of KOSPI's market capitalization — sharing the same AI-hyperscaler-capex cycle as US mega-cap tech and semiconductor names (Bloomberg, CNBC, Yahoo Finance, July-August 2026 reporting). Concrete same-session co-movement events occurred during this period (e.g., a mid-2026 session where SK Hynix fell 15%, KOSPI fell 8%, and NASDAQ-100 fell 1.88% the same day), and analysts explicitly frame this as a regime change from KOSPI's historically low, diffuse correlation with US markets to a concentrated, mechanism-driven linkage.

This raises two distinct, testable questions neither the sibling idea nor any paper found in the Phase 1 landscape scan addresses: (1) does adding *any* cross-market/global-index channel to a KOSPI LLM trading agent have positive marginal value, and (2) if global linkage matters, should the agent's channel represent it as a **blanket index-to-index correlation** (the naive, commonly-used formulation in classical finance and the closest related paper) or as a **concentration-weighted mechanistic signal** tied to the specific globally-exposed constituents actually driving the linkage (Samsung + SK Hynix vs. their US analogs)? The closest related work, CrossAlpha (arXiv 2605.29286), builds cross-market firm-pair signals from *annual-report disclosure similarity* across US/Japan/Taiwan/Korea/HK — a fundamentally different mechanism (textual/fundamental similarity, not real-time index or exposure co-movement) — so it does not resolve either question.

## Hypothesis

**H1 (channel value):** Either global-linkage channel formulation (blanket index correlation or concentration-weighted mechanistic exposure) has a positive marginal Sharpe/return contribution over the D1 (English-news) baseline when added as a 6th channel axis to the existing D0-D5 harness.

**H2 (formulation):** The concentration-weighted mechanistic formulation (b) — built only from Samsung Electronics' and SK Hynix's co-movement with a US AI-capex proxy (SOX index / hyperscaler-capex-linked basket), weighted by their KOSPI free-float market-cap shares — captures more of the marginal decision value than the blanket KOSPI-index-vs-NASDAQ-100 correlation (a), and generalizes better in historical windows where the two names still moved with US semis even though *broad* KOSPI-NASDAQ correlation was low.

**H3 (regime moderator):** The marginal value of the global-linkage channel (either formulation) is larger during the empirically documented 2026 high-correlation regime than in earlier (pre-2025) low-correlation windows within the same 2024-01 to 2026-08 backtest period — tested directly from the study's own rolling KOSPI-NASDAQ correlation series, not as a separately-asserted regime label.

## Approach sketch

**Harness reuse.** Slot D6 into the existing [[kospi-information-diet-vs-reasoning-scaffold]] 5-channel × 4-orchestration harness as a 6th channel axis, holding fixed everything that harness already controls: model backbone, prompt skeleton, JSON output schema, universe (15 KOSPI large-caps + KODEX 200), period (2024-01 → 2026-08 walk-forward, 2023-H2 warm-up), execution engine, and transaction-cost model. D6 is additive over D0 exactly like D1-D4.

**Two channel formulations, each with a raw-feature vs. specialist-agent sub-ablation (mirroring the sibling idea's D4 raw-vs-agent pattern):**
- **D6a (blanket):** overnight NASDAQ-100/SOX/S&P 500 futures returns, USD/KRW, VIX as the rolling correlation/beta of the KOSPI index itself against NASDAQ-100.
- **D6b (mechanistic):** `r_mech,t = w_Samsung · corr(Samsung_return, SOX_return)_[t-60,t] + w_SKHynix · corr(SKHynix_return, SOX_return)_[t-60,t]`, where `w_i` are each stock's KOSPI free-float market-cap weight renormalized across just the two names, correlations on a rolling 60-day window of daily returns, with rolling same-day beta against SOX reported alongside as a robustness check. All raw ingredients (Samsung/SK Hynix returns, SOX index, KOSPI cap weights) are free public data already adjacent to the existing harness's data pipeline.
- Each of D6a/D6b is tested both as a raw numeric feature appended to context and via a single frozen-backbone specialist agent that verbalizes/structures the same numbers before the trader sees them (no fine-tuning; identical backbone across all cells, consistent with the sibling harness's controls).

**Core comparisons:** D6a-O0 vs D0-O0 and D6b-O0 vs D0-O0 (H1); D6a vs D6b at matched orchestration level (H2); `Δ(D6, high-corr window) vs Δ(D6, low-corr window)` computed from the study's own rolling KOSPI-NASDAQ correlation series (H3).

**Generalization robustness arm (lightweight, not a second study):** replicate the D6a-vs-D6b head-to-head on 4 corner cells (D6a/D6b × O0/O3) using TAIEX, which has an analogous concentration mechanism (TSMC + the semiconductor cluster dominate TAIEX market cap and share the same US AI-capex cycle) — tests whether "mechanistic beats blanket" is KOSPI-idiosyncratic or reflects a general concentrated-global-exposure phenomenon, without over-claiming broad cross-market generality.

**Controls:** placebo shuffled correlation series (expect the D6 marginal value to vanish); leakage checks ensuring overnight/futures data respects KOSPI decision-time cutoffs; a US-market cross-check confirming the underlying co-movement direction on a matched US-name subsample.

## Novelty argument

No LLM multi-agent trading paper found in the Phase 1/3 search ablates a dedicated global/foreign-index-correlation channel for a non-US market, nor asks whether "global market correlation" should be represented at the index level (the default in classical finance, e.g. Ou 2023's Asia-Pacific-ETF-vs-S&P500 predictability result) or at a concentration/exposure-weighted level tied to the actual transmission mechanism. CrossAlpha (arXiv 2605.29286) is the closest adjacent paper but operates on annual-report disclosure similarity between firms, not real-time index or exposure co-movement, and does not ablate channel formulations inside a decision-making agent pipeline. DeltaLag (arXiv 2511.00390) establishes that *dynamic* lead-lag structure beats fixed/statistical baselines for portfolio construction, but is not LLM-agent-based and not applied cross-country; this idea deliberately uses simpler rolling correlation/beta rather than a trained DeltaLag-style model to keep the contribution's infrastructure cost low and reuse the sibling harness directly (a companion idea, [[llm-verbalized-vs-raw-dynamic-lead]], pursues the DeltaLag-style dynamic-signal question as its own separate, more ML-infrastructure-heavy contribution). H3's regime-moderator test is grounded in a real, sourced, concurrent 2026 market event rather than a synthetic or historical-only regime split, which is itself a distinguishing feature relative to prior regime-conditional trading-agent studies.

Cross-model review (Review LLM, hard/method focus) converged to 8/10 / verdict "ready" after one rebuttal round, having initially raised (and resolved via rebuttal) concerns about the mechanistic-signal formula being underspecified, the LLM-agent role being unclear, apparent overlap with the sibling idea, and the empirical basis for the 2026 regime claim. Two minor points remained open at convergence: a short discussion of how D6 might interact with D0-D5 (addressed above by noting all interactions are purely additive by harness design), and whether the TAIEX check licenses broader generalization claims (intentionally scoped to that one matched-mechanism market only).

## Target venue

ICAIF 2026 (ACM International Conference on AI in Finance) as primary — direct fit for a market-specific information-channel evaluation contribution grounded in a real, dated market event. EMNLP 2026 FinNLP workshop as a fallback if the cross-market signal-formulation result carries the paper. NeurIPS 2026 Generative-AI-in-Finance workshop as a further fallback.

## Risks

**Feasibility: HIGH.** This idea reuses the sibling harness's infrastructure entirely; the only new engineering is data collection for SOX/NASDAQ-100/S&P 500 futures, USD/KRW, VIX, and Samsung/SK Hynix returns (all free, public data) plus computing rolling correlation/beta — no new model training.

1. **Regime split relies on the study's own limited 2024-2026 window.** Only one clear high-correlation sub-period (2026) exists inside the pre-registered backtest window; the low-correlation baseline is necessarily an earlier, shorter sub-window, which limits statistical power for H3's interaction test. Mitigation: report effect size and bootstrap CI rather than relying on a binary significance threshold, consistent with the sibling harness's existing statistical-reporting conventions.
2. **Relationship to [[kospi-regime-adaptive-dag-rl-trading]]** (an active wiki idea that varies orchestration *topology* by detected regime) must be kept clearly distinct in any eventual write-up: that idea varies which orchestration DAG runs per regime, this idea varies which information channel is present and whether channel value itself is regime-dependent — a different factor, not a duplicate, but reviewers may conflate the two without an explicit "relationship to other wiki ideas" note.
3. **Concentration mechanism (D6b) is itself time-varying** — if Samsung/SK Hynix's combined KOSPI weight or their correlation to SOX shifts structurally again, D6b's formula (fixed 60-day rolling window, cap-weighted) may need re-tuning; this is noted as a limitation rather than resolved within scope.
4. **TAIEX robustness arm depends on data availability** for TSMC and the Taiwan semiconductor cluster's cap weights and returns; if unavailable within budget, the arm can be dropped without invalidating the primary KOSPI-only claims (H1-H3).

## Pilot results

(Leave blank — filled in by /exp-pilot-eval in Phase 5.)

## Lessons learned

(empty — filled by /exp-eval after the idea reaches a terminal status)

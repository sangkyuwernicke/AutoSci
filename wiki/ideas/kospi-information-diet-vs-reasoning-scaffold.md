---
title: "Information Diet vs Reasoning Scaffold: Ablating What Actually Transfers When US LLM Trading Agents Move to KOSPI"
slug: kospi-information-diet-vs-reasoning-scaffold
status: proposed
origin: "ideate: user-directed edge — US-built LLM multi-agent trading research emphasizes ever-smarter agent debate/coordination; the claim to test is that on KOSPI, adapting the INPUT DATA channels to the market matters more than the reasoning scaffold. Grounded in the AMA architecture>backbone finding, FINSABER regime-shift blindness, and the unablated memory/debate/persona gaps. Simplified 2026-09-28 from a 24-cell (6 diet × 4 scaffold) full ablation atlas down to a single 2×2 (4-cell) core design, per advisor guidance to center the paper on one sharp claim rather than a broad atlas — see 'Scope note' below."
origin_gaps: ["[[llm-multi-agent-financial-trading]]", "[[agentic-trading]]", "[[llm-finance]]"]
tags: [kospi, llm-multi-agent-financial-trading, ablation-study, market-transfer, information-channels, evaluation-methodology, korean-market]
target_venue: ICAIF 2026 / EMNLP 2026 (FinNLP) / NeurIPS 2026 Workshop on Generative AI in Finance
novelty_score: 3
priority: 5
pilot_result: "pass — 4 cells (D1_S0, D1_S3, D5_S0, D5_S3) completed cleanly with 0-6.7% JSON parse-failure (all <10% pass threshold); qualitative trace confirms both diet (DART/flow content referenced) and scaffold (debate genuinely changes outcome) channels are used; cumulative returns 2.47-3.65% across cells vs 3.78% Buy&Hold benchmark at pilot scale (5 days/3 names/1 seed) — infrastructure validated, sample too small to test H1/H2, proceed to full study"
failure_reason: ""
linked_experiments: [kospi-information-diet-vs-reasoning-scaffold, kr-replication-tradingagents-kospi-stage1, kospi-replication-baseline]
date_proposed: 2026-08-31
date_resolved: ""
---

## Motivation

LLM multi-agent trading research is dominated by work on the *reasoning scaffold* — how to make agents debate better ([[tradingagents-framework]]'s bull/bear researcher debate), coordinate better ([[fincon-framework]]'s manager-analyst hierarchy), or remember better ([[tradinggpt-framework]]'s layered memory). Yet [[when-agents-trade-live-multi-market]] (Agent Market Arena) finds that in live trading, *agent architecture* — not LLM backbone — drives performance, and no paper has isolated whether that architectural benefit is real signal processing or compensation for an impoverished input. Three wiki gaps converge here:

- "[[tradinggpt-multi-agent-system-layered-memory]]: how much of the benefit comes from layered memory vs. character diversity vs. debate — no ablation isolates these three components."
- "[[orchestration-framework-financial-agents-algorithmic-trading]]: what is the marginal contribution of each agent pool? Can ablations isolate memory vs. orchestration vs. risk gating?"
- "[[llm-multi-agent-financial-trading]] known limitation: agent communication design critically affects performance but is rarely ablated."

KOSPI is the ideal stress environment for this question. Its information ecosystem differs structurally from the US one every US framework was tuned against: (1) daily foreign / institutional / retail net-flow series are public, watched, and predictive of volatility (arXiv 2508.20426); (2) DART filings are mandatory, Korean-language, and minute-timestamped, arriving before English coverage; (3) chaebol earnings cluster in Q1/Q3; (4) retail participation is far higher than in the US. US frameworks feed on an *institutional* information diet — analyst reports, earnings calls, English newswire, quarterly filings — and may systematically miss the retail/flow-driven dynamics that move KOSPI. The evaluation window also contains a genuine live regime break (2024 AI rally → 2026-07 KOSPI plunge), letting us test [[when-agents-trade-live-multi-market]]'s and [[tradingagents-multi-agents-llm-financial-trading]]'s open question of whether these systems survive a bear transition.

## Scope note (2026-09-28)

Original scope crossed a 6-level information-diet axis against a 4-level reasoning-scaffold axis (24 cells), plus a behavioral sub-study (H3) and a secondary KOSDAQ universe. Per advisor guidance — one sharp claim, not a broad atlas — the design is cut down to the **4-cell (2×2) core** that already answers the primary hypothesis directly, using cells that were previously flagged as the "corner cells" for strong-backbone replication. Everything not needed to defend that single claim is deferred to future work (see "Cut from scope" at the end). This does not weaken H1/H2 — both are answerable from exactly these 4 cells — it removes the secondary decomposition and behavioral analyses that were separate stories bundled into the same idea.

**Update (2026-09-29):** the 4-cell design is KOSPI-only — D1 is *not* "the framework running on US stocks," it is the same KOSPI tickers fed a naive/translated diet. A reviewer could ask whether a null or shrinking scaffold effect on KOSPI is a real market-transfer finding or just this particular reimplementation being weak in general — the natural check being "does the scaffold actually help on its home market?" Briefly considered adding a 2-cell US cross-check (US_S0/US_S3) to answer this directly, then reverted: [[tradingagents-multi-agents-llm-financial-trading]] (the source paper for the base framework used here) already reports the full-scaffold system beating rule-based baselines with very high cumulative return (23–27%/3mo) and Sharpe (5.6–8.2) on its original US evaluation — published, independent evidence that the scaffold has positive value on its home market. Re-running that same check ourselves would be redundant. **Design stays at 4 cells (D1/D5 × S0/S3), KOSPI-only.** The paper should cite the TradingAgents US results directly when addressing this reviewer question, rather than re-deriving them.

## Hypothesis

**H1 (primary, and the paper's single claim):** On KOSPI, the marginal performance contribution of adapting the *information diet* to the market (Korean-native news, DART disclosures, investor net-flow channel, combined) exceeds the marginal contribution of the *reasoning scaffold* (bull/bear debate, risk-team deliberation, hierarchical manager consolidation) that US frameworks emphasize. Concretely: a flat single-agent system on a Korea-adapted diet (D5·S0) matches or beats a full multi-agent system on the naive transfer diet (D1·S3) — the head-to-head that directly pits diet-improvement against scaffold-improvement.

**H2 (interaction, free corollary of the same 4 cells):** The value of the reasoning scaffold *shrinks* as the information diet becomes Korea-appropriate — `ΔScaffold(D5) < ΔScaffold(D1)`, where `ΔScaffold(D) = M(D,S3) − M(D,S0)`. No extra cells are needed beyond the 4 below; this is read directly off the same grid.

## Approach sketch

**Base framework.** [[tradingagents-framework]] (public repo, clean role separation, structured/NL hybrid communication, no portfolio-optimization step to confound scaffold ablation).

**A single 2×2 = 4-cell design, not a full grid.**

*Diet axis — two levels only:*
- **D1** naive transfer diet: price/technical + machine-translated English news + quarterly earnings — "just run [[tradingagents-framework]] on Korean tickers"
- **D5** Korea-adapted diet: D1 with Korean-native news (not translated) + a DART-disclosure-reading agent (OpenDART; rights offerings, treasury stock, 5%-rule holdings, supply contracts, earnings pre-announcements) + investor net-flow channel (foreign/institutional/retail daily net buys, 20-day lookback), combined as one bundle

*Scaffold axis — two levels only:*
- **S0** single agent, one call: all inputs → buy/sell/hold
- **S3** minimal reimplementation of the [[tradingagents-framework]] role structure (not the published package, to bound cost): 4 parallel specialist analysts → one combined bull/bear debate call → trader → one combined risk-team + manager call (7 LLM calls per decision)

**Universe & period.** 15 KOSPI large caps + KODEX 200. 2024-01 → 2026-08 walk-forward, 2023-H2 warm-up. Regime split (bull / transition-crash / recovery) pre-registered before any run, used only to report the result by sub-period, not as an extra ablation axis.

**Backtest realism (kept — cheap and load-bearing for credibility).** 0.20% transaction tax (2026), slippage, KRW commission; ±30% daily price-limit modeling; long-only; delisted names retained; strict news/disclosure timestamp < decision time. Single backbone (GPT-4o-mini or Qwen3-8B) for the primary result. 5 seeds per cell (only 4 cells, so this is inexpensive).

**Quantities computed (standard metrics only: Sharpe, Sortino, MDD, CVaR, cumulative return):**
- `ΔData(S) = M(D5,S) − M(D1,S)` — value of Korea-adapting the input, per scaffold level
- `ΔScaffold(D) = M(D,S3) − M(D,S0)` — value of the scaffold, per diet level
- **H1 test:** is `ΔData(S0) ≥ ΔScaffold(D1)`? Bootstrap CI over the 5 seeds.
- **H2 test:** is `ΔScaffold(D5) < ΔScaffold(D1)`? Bootstrap CI on the difference.

**One control kept (cheap, directly defends validity).** Shuffled disclosure timestamps on D5 → expect the DART/flow-channel benefit to vanish, confirming no look-ahead leakage into the headline result.

**Deliverable.** A single figure: a 2×2 bar chart of the four cells' Sharpe (or cumulative return), plus the two Δ comparisons. One open-source KOSPI data loader (KRX OHLCV + investor flows, OpenDART, Korean-news loader, look-ahead guard) as a secondary artifact.

## Novelty argument

The "port a multi-agent LLM trading framework to a non-US market + ablate agent roles" genre already exists — Japanese equities (arXiv 2602.23330, fine-grained task decomposition + agent ablation) and Chinese public REITs (arXiv 2602.00082, single framework + general-vs-fine-tuned-backbone comparison). Both ablate the *scaffold* on a single regime. This idea differs on the axis that matters:

1. **The contrast is diet vs scaffold, not role-A vs role-B.** No prior LLM-trading paper crosses an *information-channel* ablation against a *coordination-complexity* ablation and computes their relative marginal value — even reduced to the minimal 2×2 test, this is a direct, falsifiable challenge to the field's focus on debate/coordination design and to AMA's "architecture is what matters" framing (it may be that architecture only matters because the input was wrong).
2. **Live regime break, not backtested regime slices.** This evaluates a system through a real bull→bear transition inside the deployment window, at no added design cost (the window is used as-is, only reported by sub-period).
3. **KOSPI-specific channels that are mechanistically motivated, not cosmetic.** Investor net-flow and DART disclosure are not "Korean versions of US news" — they are information types with no clean US analog, tied to KOSPI's retail dominance and mandatory-disclosure regime.

**Closest existing work that is NOT this paper:**
- **TradingAgents-KR** (GitHub malda231125, July 2026, Stars: 7): connects TradingAgents to KIS/DART/ECOS/Naver News as a research tool. Not a paper — no ablation, no evaluation, no comparison between channel configurations.
- **PRISM-INSIGHT** (HN Nov 2025): 13-agent Korean stock analyzer, 8-month live simulation. Not a paper — no controlled comparison between information configurations, no scaffold vs. diet measurement.

Both show that practitioners are building Korean-market LLM trading systems. Neither asks "which component actually contributes" — that gap is exactly what this paper fills.

Closest residual risk: reviewers may read a 4-cell design as thin, and may ask whether the naive-diet condition (D1) is meant to represent the framework's US-market performance — it is not; D1 is KOSPI-with-a-naive-diet. Mitigation — the sharpness of a single pre-registered hypothesis with a clean falsification control (shuffled-timestamp placebo) is itself a strength for a workshop/short-paper framing, the open data loader is a standing artifact independent of cell count, and the "what about the US market?" question is answered by citing [[tradingagents-multi-agents-llm-financial-trading]]'s own published US results (strong scaffold performance vs. rule-based baselines) rather than by re-running a redundant cross-check.

## Target venue

ICAIF 2026 (ACM International Conference on AI in Finance) as primary — strong fit for market-specific evaluation contributions, and the tight single-claim design suits ICAIF's shorter paper tracks well. EMNLP 2026 FinNLP workshop if the Korean-language-channel result carries the paper. NeurIPS 2026 Generative-AI-in-Finance workshop as a fallback.

## Risks

**Feasibility: LOW-MEDIUM** (reduced from MEDIUM — the 24-cell cost driver is gone).

1. **Korean-language news data is the critical dependency.** No single free bulk source. Candidates: BigKinds (Korea Press Foundation news big-data, research access), AI-Hub financial-news datasets, Naver News API (rate-limited). Must be resolved before the pilot; the CoT-ETF paper's ~94k-headline source is the first lead to chase. If unavailable, D5's Korean-news component degrades to "headline-only" and the diet-channel result weakens.
2. **Single base framework (TradingAgents).** A null scaffold result might be TradingAgents-specific. Not addressed by an additional framework in this scope (deliberately deferred — see below) — flag explicitly as a limitation in the paper rather than scope-expand to cover it.
3. **DART disclosure parsing** (Korean, semi-structured filing types) is non-trivial engineering; look-ahead control on filing timestamps must be exact — this is now the main remaining engineering risk, since the cost/scale risk of the full grid is gone.
4. **LLM leakage** on 2024 KOSPI moves; partially handled by reporting the 2026-07 crash sub-window separately, but never fully eliminable with a closed backbone.

## Cut from scope (kept here for traceability, not pursued now)

- **Per-channel decomposition** (D2 Korean-news-only, D3 DART-only, D4 flow-only, and the D0 price-only floor) — the "which channel contributes how much" story. Candidate follow-up paper if D5 vs D1 shows a strong effect.
- **Intermediate scaffold levels** (S1 parallel-analysts-no-debate, S2 debate-without-risk-team) — needed only for a continuous dose-response scaffold curve, not for the binary H1/H2 claim.
- **H3 (behavioral bias reduction, tied to FINSABER's "bull-timid/bear-reckless" finding)** — separate behavioral-analysis story; also currently under-supported because FINSABER (arXiv 2505.07078) has not been ingested into this wiki as its own page (see review below). Do not cite it as a load-bearing claim until ingested and verified.
- **Secondary KOSDAQ mid-cap robustness universe** — nice-to-have generalization check, not needed for the core claim.
- **Coordination Breakeven Spread metric** (from arXiv 2603.27539) — non-standard metric; standard Sharpe/Sortino/MDD/CVaR/return already carry the claim.
- **Variance decomposition (mixed-effects model)** — only useful with the full grid; with 4 cells, simple bootstrap CIs on the two Δ's are sufficient and simpler to defend.
- **Light US cross-check** (5 matched US names) — briefly reconsidered 2026-09-29 in response to a reviewer-facing question ("shouldn't D1 be benchmarked against the US market, e.g. S&P?"), then confirmed as genuinely redundant rather than just deferrable: [[tradingagents-multi-agents-llm-financial-trading]] already reports the full-scaffold system's strong US-market performance vs. rule-based baselines (23–27%/3mo return, 5.6–8.2 Sharpe), i.e. independently published evidence that `ΔScaffold(US) > 0` on its home market. Cite that result directly in the paper instead of re-running the check.
- **Classical (non-LLM) algorithmic-trading baseline** — raised by the cross-model review below as a real gap, but adding it would re-expand scope; note it explicitly as a limitation in the paper instead of closing it here.

## Pilot results

Verdict: **PASS** (infrastructure validation only). Linked experiment: [[kospi-information-diet-vs-reasoning-scaffold]]. Code: `experiments/code/kospi-information-diet-vs-reasoning-scaffold/`; spec and report: `experiments/pilot/kospi-information-diet-vs-reasoning-scaffold.yaml` and its `report.md`.

Setup: 1 seed, 5 trading days, 3 names; S3 is the minimal 7-call reimplementation, not the published TradingAgents package.

| Cell | Cumulative return | Sharpe | MDD | Parse-failure rate | LLM calls |
|---|---|---|---|---|---|
| D1_S0 | 3.65% | 6.31 | -2.04% | 6.7% | 16 |
| D1_S3 | 2.71% | 7.39 | -1.19% | 0% | 112 |
| D5_S0 | 2.58% | 4.73 | -2.32% | 0% | 15 |
| D5_S3 | 2.47% | 8.01 | -0.98% | 0% | 105 |
| Buy & hold (benchmark) | 3.78% | 3.71 | n/a | n/a | 0 |

Diagnostic deltas (not statistically powered): ΔData(S0) = -1.07pp, ΔScaffold(D1) = -0.94pp, ΔScaffold(D5) = -0.11pp. The sample is too small to test H1/H2; the pilot only shows that all four cells run cleanly, the channels are structurally distinct (`input_present` True for DART/flow on D5, False on D1), and S3 responds to analyst/debate content.

Open items before the full study: a bulk Korean-language news source (the pilot used a hand-curated stub of about 5 headlines) and re-running the improved DART body extraction through the LLM pipeline. Status stays `proposed` (a pilot pass does not transition status).

## Lessons learned

(empty — filled by /exp-eval after the idea reaches a terminal status)

## Review history

- **2026-09-28** — `/review` (Review LLM, deepseek/deepseek-chat, standard difficulty, comprehensive focus) on the pre-simplification 24-cell version. Score 7/10, verdict `needs-work`. Key findings: (1) no classical AT baseline — noted above as an accepted limitation rather than closed, to keep scope tight; (2) single-framework (TradingAgents) generalizability — accepted as a stated limitation, not addressed in this scope; (3) FINSABER (arXiv 2505.07078) cited but not ingested into the wiki — resolved here by removing FINSABER as a load-bearing citation (it only supported the now-cut H3); (4) Korean-news data dependency and LLM-leakage risk — both carried forward unchanged in the Risks section above. The scope cut in this revision directly addresses the review's implicit "too broad" pressure (24 cells, 3 hypotheses) even though the review itself asked for additions (baseline, second framework) rather than cuts — those additions are recorded as accepted limitations, not pursued, per the advisor's simplicity preference.

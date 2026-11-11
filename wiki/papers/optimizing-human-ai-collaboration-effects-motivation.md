---
title: "Optimizing Human-AI Collaboration: Effects of Motivation and Accuracy Information in AI-Supported Decision-Making"
slug: optimizing-human-ai-collaboration-effects-motivation
arxiv: ""
venue: "Computers in Human Behavior: Artificial Humans"
year: 2023
tags:
  - human-ai-collaboration
  - trust-calibration
  - explainable-ai
  - decision-making
  - motivation
  - behavioral-experiment
importance: 3
date_added: 2026-05-29
source_type: pdf
s2_id: ""
tldr: "Motivation (via gamification) and accuracy information each independently improve human-AI decision-making quality by facilitating better trust calibration, but combining them yields no additional benefit."
contribution_type:
  - analysis
  - benchmark
datasets: []
cited_by: []
---

## Problem & Context

Human-AI (HAI) collaboration is mandated in high-stakes domains (e.g., personnel selection, medicine) by regulations such as the GDPR and the proposed EU AI Act, yet empirical research consistently shows that HAI teams underperform AI systems operating alone. Explainable AI (XAI) techniques — intended to make AI recommendations more transparent and improve user trust — have so far failed to reliably improve joint decision quality. Before this paper, the field lacked a clear account of *why* XAI approaches underperform: the prevailing assumption was that transparency alone should suffice.

## Key idea

Using dual process theory (Chaiken 1980; Strack & Deutsch 2004), the authors argue that XAI is only beneficial when users process explanations *systematically* (deliberately) rather than *heuristically* (via cognitive shortcuts). Two levers can induce more deliberate processing: (1) **extrinsic motivation** (implemented as gamification via a leaderboard) and (2) **accuracy information** (AI self-reported confidence labels, colour-coded high/low). Both are predicted to independently improve HAI performance by enabling better-calibrated trust — neither over-trusting nor under-trusting the system.

## Method

A 2 × 2 between-participants online experiment (N = 337 German working adults; M_age = 55.17 yrs; non-commercial research panel) with one within-participant factor (AI recommendation quality: high vs. low). Conditions: (i) control, (ii) gamification only, (iii) accuracy information only, (iv) both. All participants rated simulated job applicants (scale 1–100) and received an AI recommendation plus feature-importance explanation. High-quality AI recommendations deviated ≤ 5 points from the optimal score; low-quality recommendations deviated 20 points and were accompanied by deliberately misleading feature importance explanations. Performance = absolute deviation of participant rating from optimal score (lower is better; baseline = 10 if always following the AI). Gamification: leaderboard promise. Accuracy information: green/red text labels on AI confidence.

## Experiment & Results

All analyses used Python 3.10 or R 3.6 with mixed ANOVA (2 between × 1 within factors).

**Manipulation check**: Gamification did not raise self-reported motivation (F(1,335) = 0.15, p = .69) but did improve performance, suggesting behavioural rather than introspective effects.

**Recommendation quality** (H0): Participants performed significantly worse on low-quality AI rounds (F(1,336) = 46.80, p < .001, η² = 0.067) and deviated more from low-quality recommendations (F(1,336) = 41.50, p < .001, η² = 0.389), confirming they detected some AI errors.

**Motivation (H1.1 — supported)**: High-motivation participants performed significantly better overall (F(1,333) = 4.43, p < .01, η² = 0.003). Crucially, the improvement was specific to high-quality AI rounds (interaction: F(1,333) = 40.83, p < .01, η² = 0.06) — motivated participants trusted good recommendations more, not errors less. Mean performance (low-quality rounds): motivated 10.06 vs. not motivated 9.80; high-quality rounds: 6.90 vs. 8.14.

**Need for cognition moderation (H1.2 — not supported)**: No moderation effect (F(1,335) = 0.05, p = .82). The sample had unusually high need for cognition (M = 5.18/7), creating a ceiling effect.

**Accuracy information (H2 — supported)**: Accuracy information improved performance (F(1,333) = 4.50, p < .01, η² = 0.013) and — unlike motivation — this improvement was similar for both high- and low-quality rounds (no interaction: F(1,333) = 1.06, p = .30). Mean performance (high-quality): 7.02 vs. 8.06 without accuracy info; (low-quality): 9.82 vs. 10.06.

**Combination (H3 — not supported)**: Adding both motivation and accuracy information did not yield incremental gains (interaction: F(1,333) = 2.93, p = .08). The effects appear interchangeable rather than additive.

**Trust**: Neither manipulation affected self-reported trust (motivation: p = .05; accuracy info: p = .05), but both influenced behavioural trust (deviation from AI recommendation). Motivated participants trusted high-quality recommendations more (F(1,333) = 4.47, p < .05); accuracy information shifted trust bidirectionally — less trust in low-quality, more trust in high-quality outputs (F(1,333) = 8.28, p < .01, η² = 0.009).

## Limitations

- Self-reported trust and motivation did not reflect condition differences, suggesting introspection limits or order effects (measured only post-task).
- Sample skewed toward high need for cognition (research panel volunteers), limiting variance needed to detect moderation.
- No causal decomposition: it is unclear whether improved performance required the XAI explanation or whether a bare recommendation would suffice.
- Limited experience with AI and personnel selection; findings may not generalise to domain experts.
- Simulated task with deterministic optimal score; ecological validity to real-world HAI contexts uncertain.
- The combination condition failure may reflect that accuracy information renders motivational effort redundant only when accuracy cues are perfectly reliable.

## Open questions

- Do incremental effects of motivation + accuracy information appear when accuracy information is imperfect or noisy?
- How do continuous motivation and trust trajectories evolve within trials, especially after a detected AI error?
- Would a more diverse population (varying need for cognition) show the predicted moderation effect?
- Are the mechanisms (motivation improving trust calibration, accuracy information improving both over- and under-trust) independent or mediated by shared cognitive load reduction?
- How does growing real-world experience with AI systems shift these effects over time?

## My take

A clean, well-controlled study that pins down *when* explanations help: only under motivated, systematic processing. The asymmetry between motivation (helps with high-quality recs only) and accuracy information (helps with both) is the most practically actionable finding. The non-additivity result is a useful cautionary note against stacking interventions. The trust measurement gap (behavioural vs. self-report divergence) highlights an underappreciated measurement problem in the field. Importance is moderate — the contribution is empirical refinement rather than a conceptual or methodological breakthrough.

## Related

- [[trust-calibration-human-ai-collaboration]]

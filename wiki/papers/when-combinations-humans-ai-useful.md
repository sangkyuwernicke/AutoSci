---
title: "When combinations of humans and AI are useful"
slug: when-combinations-humans-ai-useful
arxiv: "2405.06087"
venue: "arXiv preprint"
year: 2024
tags:
  - human-AI collaboration
  - meta-analysis
  - systematic review
  - human-AI synergy
  - decision-making
  - generative AI
importance: 5
date_added: 2026-05-29
source_type: tex
tldr: "A pre-registered systematic review and meta-analysis of 106 experiments finds that human-AI combinations are, on average, worse than the best of humans or AI alone (Hedges' g = -0.23), but creation tasks and settings where humans outperform AI yield positive synergy."
contribution_type:
  - analysis
  - survey
datasets: []
cited_by: []
---

## Problem & Context

As AI tools proliferate across medicine, finance, law, and daily life, a fundamental question has gone unanswered: when do human-AI combinations actually outperform either humans or AI working alone? The field is fragmented — some studies report large gains from human-AI teaming while others show that adding humans to AI pipelines hurts performance. This heterogeneity makes it impossible to draw principled conclusions about when to integrate humans into AI systems.

Prior literature reviews on human-AI collaboration were qualitative, or focused narrowly (e.g., only explainability studies, only comparing to humans-alone). The lack of a quantitative synthesis using a rigorous "best-of-humans-or-AI" baseline meant the field lacked ground truth about whether human-AI synergy — defined analogously to synergy in human teams — actually exists.

## Key idea

The paper distinguishes two outcome concepts: **human-AI synergy** (human-AI combination beats both human alone and AI alone — analogous to strong synergy) and **human augmentation** (human-AI combination beats human alone only). The key finding is that on average across recent experiments, **human-AI synergy does not exist** — the combined system underperforms the better of the two. However, the sign flips depending on two critical moderators: task type (decision vs. creation) and the relative performance of humans vs. AI alone.

The roadmap insight is actionable: creation tasks (especially generative AI) offer the most promise for synergy; decision tasks under the current paradigm yield losses; and researchers have been over-investing in AI explanations and confidence displays that empirically don't move the needle.

## Method

**Systematic review and meta-analysis.** The authors searched ACM DL, AISeL, and Web of Science for experiments published January 2020–June 2023 that reported performance of (1) human alone, (2) AI alone, and (3) human-AI system simultaneously. After applying inclusion/exclusion criteria per PRISMA guidelines and a pre-registration (OSF), 74 papers yielding 106 unique experiments and 370 effect sizes were identified.

**Effect size calculation.** Hedges' g was computed for each condition: for synergy, the baseline is whichever of human-alone or AI-alone performed better; for augmentation, the baseline is human-alone.

**Three-level random-effects meta-analytic model.** Effect sizes are nested within experiments (accounting for multiple treatments per experiment) within papers. Cluster-robust variance estimation (RVE) with the Knapp-Hartung adjustment handles dependent sampling errors. Implemented in R using the `metafor` package.

**Moderator analysis.** Meta-regressions were run for each of 11 moderators: publication date, pre-registration status, experimental design, data type, task type, task output, AI type, AI explanation presence, AI confidence display, participant type, performance metric.

**Bias testing.** Funnel plots, Egger's regression, and rank correlation tests assessed publication bias. Sensitivity analyses included leave-one-out at effect-size/experiment/paper levels and outlier removal (Cook's distance > 4/N).

## Experiment & Results

**Primary result (human-AI synergy):** The pooled effect was significantly negative: Hedges' g = -0.23 (95% CI: -0.39 to -0.07), t(92) = -2.89, p = 0.005. Human-AI combinations are, on average, *worse* than the best-performing individual agent.

**Human augmentation:** The pooled effect was significantly positive: g = 0.64 (95% CI: 0.53 to 0.74), t(98) = 11.87, p < 0.001 — human-AI systems do beat humans alone on average.

**Heterogeneity:** I² = 97.7% for synergy, 93.8% for augmentation — enormous unexplained variance.

**Moderator: task type.** Decision tasks: g = -0.27 (p = 0.002). Creation tasks: g = +0.19 (p = 0.18, n.s. but directionally positive and significantly different from decision tasks, F(1,104) = 7.84, p = 0.006).

**Moderator: relative human/AI performance.** When human > AI alone: synergy g = +0.46 (95% CI: 0.28–0.66). When AI > human alone: synergy g = -0.54 (95% CI: -0.71 to -0.37). F(1,104) = 81.79, p < 0.001.

**Non-significant moderators:** AI explanation presence, AI confidence display, participant type (lab/crowd/expert). These null results challenge the emphasis on explainability in recent HCAI work.

**Significant secondary moderators:** AI type (F(2,103) = 3.77, p = 0.026); year of publication (F(3,102) = 3.65, p = 0.015).

**Bias:** No significant publication bias for synergy. Evidence of publication bias *favoring* human augmentation results (Egger's: β = 1.96, p = 0.002).

**Robustness:** All sensitivity analyses (paper-level clustering, outlier removal, estimated-value exclusion, leave-one-out) yielded comparable results, confirming the main finding.

## Limitations

1. Inclusion criterion requiring all three conditions (human alone, AI alone, human-AI) excludes tasks neither agent can do alone — potentially understating achievable synergy.
2. Hedges' g pools across very different metrics (accuracy, quality, error rates), introducing noise.
3. Heterogeneous samples (doctors, crowdworkers, students) vary in skill and motivation in ways not fully captured by moderators.
4. Variable measurement precision across studies (some estimate accuracy on 15 items, others on 500).
5. Potential research topic selection bias: the configurations researchers choose to study may not be representative of deployed AI systems.
6. High residual heterogeneity (I² > 97%) suggests important moderators — possibly interaction effects — remain unmeasured.
7. Evidence of publication bias toward human augmentation results.

## Open questions

- Can creation-task synergy be reliably replicated with generative AI (LLMs)? Most generative AI studies to date only report human-alone vs. human+AI, omitting AI-alone as a baseline.
- What interaction effects exist between moderators (e.g., task type × explanation presence)?
- How should commensurability criteria (standardized benchmarks, incentive schemes, evaluation metrics) be implemented across HCAI studies?
- Does the relative-performance moderator generalize beyond majority-vote decision tasks to sequential workflows and co-creation pipelines?
- Can composite evaluation metrics (e.g., incorporating rare-error costs) change the synergy picture in high-stakes domains?

## My take

This is the most rigorous quantitative synthesis of human-AI collaboration to date. The headline finding — human-AI combinations underperform the best-alone agent — is important and counterintuitive for many practitioners who assume that "human in the loop" is always better. The two robust moderators (task type and relative performance) are immediately actionable for experiment design. The null result on explanations/confidence is especially striking given how much NeurIPS/CHI effort goes into XAI for human-AI decision support. The arXiv preprint (2405.06087) is the earlier version; the journal version appeared in Nature Human Behaviour as [[when-combinations-humans-ai-useful-systematic]].

## Related

- [[when-combinations-humans-ai-useful-systematic]] — published Nature Human Behaviour version of this work

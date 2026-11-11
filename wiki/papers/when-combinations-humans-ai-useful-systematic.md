---
title: "When combinations of humans and AI are useful: A systematic review and meta-analysis"
slug: when-combinations-humans-ai-useful-systematic
arxiv: "2405.06087"
venue: "Nature Human Behaviour"
year: 2024
tags:
  - human-ai-collaboration
  - meta-analysis
  - systematic-review
  - human-ai-synergy
  - decision-making
  - ai-augmentation
importance: 4
date_added: 2026-05-28
source_type: pdf
s2_id: "02aec976011a7d595d61db9639209968f4b93177"
tldr: "A preregistered meta-analysis of 106 experiments finds that human–AI combinations on average underperform the better of human or AI alone, with performance losses in decision tasks but gains in creation tasks—and that relative human/AI baseline performance is the strongest moderator."
contribution_type:
  - analysis
  - survey
datasets: []
cited_by: []
---

## Problem & Context

Human–AI collaboration has been studied across medicine, finance, law, and everyday tasks, with researchers reporting wildly different outcomes—some showing synergy and others showing degradation relative to humans or AI alone. Before this paper, the field lacked a principled, quantitative synthesis capable of answering the fundamental question: under what conditions does combining a human with an AI system produce better results than either alone?

The prior literature fragmented along disciplinary lines (HCI, AI, social science), used inconsistent baselines (some compared human–AI to human-alone, omitting the AI-alone baseline), and drew qualitative rather than quantitative conclusions from individual case studies. The absence of a single unified effect-size estimate left researchers and practitioners without clear guidance on where to invest in human–AI system design.

## Key idea

Conduct a preregistered, interdisciplinary systematic review and three-level meta-analysis covering 106 experiments (370 effect sizes, 2020–2023) that each report the performance of (1) human alone, (2) AI alone, and (3) human–AI combined. Define two outcome measures: **human–AI synergy** (outperforming the better of human or AI alone) and **human augmentation** (outperforming the human alone). Use meta-regression to identify moderators that explain why some human–AI systems achieve synergy and others do not.

## Method

**Data collection.** Searched ACM Digital Library, Web of Science, and AIS eLibrary for peer-reviewed studies published January 2020–June 2023. Of 5,126 papers retrieved, 74 met inclusion criteria (original experiment, quantitative performance of all three conditions, sufficient statistics for Hedges' g computation). Those 74 papers yielded 106 unique experiments and 370 effect sizes.

**Effect size computation.** Computed Hedges' g (unitless standardized effect size) for each condition comparison, enabling cross-study aggregation despite heterogeneous outcome measures (accuracy, error rate, quality scores, etc.).

**Three-level hierarchical meta-analytic model.** Accounted for the nested structure (effect sizes nested within experiments nested within papers) using a restricted maximum-likelihood three-level model. Weighted effect sizes by inverse variance across participants.

**Moderator analysis.** Meta-regressions tested eight moderators: type of task (decision vs. creation), task output type (binary/categoric/numeric/open response), task data modality (image/text/numeric/video/multiple), relative performance of human vs. AI alone, type of AI (deep learning / shallow / Wizard of Oz), year of publication, experimental design (dependent vs. independent samples), presence of AI explanation, presence of AI confidence output, participant type (expert vs. crowdworker), and division of labour.

## Experiment & Results

**Overall synergy.** Human–AI combinations performed significantly *worse* than the better of human or AI alone: pooled effect g = −0.23 (95% CI: −0.39 to −0.07; t₉₂ = −2.89, p = 0.005). This is a small but statistically reliable negative effect. By contrast, human augmentation was strongly positive: g = 0.64 (95% CI: 0.53 to 0.74; t₉₈ = 11.87, p < 0.001), i.e., AI reliably helped humans beat their own unaided baseline, but not the AI-alone ceiling.

**Heterogeneity.** Effect sizes were extremely heterogeneous: I² = 97.7% for synergy and 93.8% for augmentation, motivating the moderator search.

**Task type moderator (p = 0.006).** Decision tasks (344/370 effect sizes) showed g = −0.27 (p = 0.002). Creation tasks (34 effect sizes) showed g = +0.19 (p = 0.180, not significant individually, but the decision–creation contrast was significant). Human–AI systems are more promising for open-ended generative tasks than for closed-set classification decisions.

**Relative human/AI performance moderator (p < 0.001).** When humans outperformed AI alone: g = +0.46 (95% CI: 0.28 to 0.66). When AI outperformed humans alone: g = −0.54 (95% CI: −0.71 to −0.37). This is the strongest moderator: humans benefit from AI collaboration most when they are already the better performer—presumably because they are also better calibrated about when to trust the AI.

**Non-significant moderators.** AI explanation (no/yes), AI confidence output (no/yes), participant expertise, and crowdworker vs. expert populations did not significantly moderate synergy or augmentation. Only 3 of 100+ experiments tested explicit task-level delegation of subtasks (division of labour), so that moderator was underpowered.

**AI type and year.** Type of AI (deep/shallow/WoZ) moderated synergy (p = 0.026); year of publication moderated synergy (p = 0.015, with more recent studies showing less synergy, possibly reflecting harder tasks or higher AI baselines).

## Limitations

1. Inclusion criteria required all three performance conditions (human alone, AI alone, human–AI), excluding potentially relevant studies where one condition was absent; tasks where neither can perform alone are unrepresented.
2. Possible publication bias (toward positive results) was not confirmed by tests, but cannot be ruled out.
3. Research topic selection bias: researchers chose tasks and participant pools that may not reflect real-world deployment conditions.
4. High residual heterogeneity (I² ≈ 97%) remains largely unexplained—interaction effects between moderators are plausible but the corpus is too small to detect them.
5. The vast majority of studies (>95%) placed humans in the role of final decision-maker after receiving AI input; more exotic collaboration architectures are underrepresented.
6. Study quality varies (attention checks, incentive structures differ), introducing noise not captured by the three-level model.

## Open questions

- What collaboration architectures (beyond "human sees AI output and decides") can unlock synergy even when AI outperforms humans?
- How does synergy scale as AI frontier models continue to improve—will the AI-outperforms-human regime expand and worsen synergy on average?
- Can a commensurability framework (standardized benchmarks, metrics, reporting protocols) for human–AI experiments accelerate systematic progress?
- What interaction effects exist between moderators (e.g., explanation × task type, AI type × relative performance)?
- How do composite performance metrics (cost-sensitive accuracy, rare-error penalties) change the synergy picture in high-stakes domains?

## My take

This is a landmark empirical synthesis that reframes the conversation in human–AI systems. The headline finding—average negative synergy—is counterintuitive and important, but the deeper contribution is the moderator analysis: AI explanation and confidence displays (which receive outsized research attention) are non-significant, while relative baseline performance and task type (which have received little attention) are the dominant factors. The paper points forcefully toward creation tasks and task-delegation designs as the underexplored frontiers. The methodological care (preregistration, three-level model, Hedges' g, three database search) is exemplary. The 97%+ heterogeneity is a reminder that a single pooled effect is insufficient; the field needs richer moderator taxonomies and better commensurability criteria.

## Related

- [[human-ai-synergy]] — the core concept defined and measured by this paper
- [[human-augmentation]] — the secondary outcome measure (human–AI vs. human alone)
- [[three-level-meta-analytic-model]] — statistical method used for effect-size synthesis

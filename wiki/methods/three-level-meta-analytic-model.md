---
name: "Three-Level Meta-Analytic Model"
slug: three-level-meta-analytic-model
type: evaluation
tags:
  - meta-analysis
  - hierarchical-model
  - effect-size-synthesis
  - human-ai-collaboration
source_papers:
  - "[[when-combinations-humans-ai-useful-systematic]]"
parent_methods: []
child_methods: []
realizes_concepts:
  - "[[human-ai-synergy]]"
  - "[[human-augmentation]]"
date_updated: 2026-05-28
---

## Problem setting

Standard pairwise meta-analyses assume all effect sizes are independent. In human–AI collaboration research, a single paper may report multiple experiments (e.g., different tasks), and a single experiment may yield multiple effect sizes (e.g., different participant subgroups or performance metrics). Ignoring this nesting inflates precision and underestimates variance.

## Mechanism

The three-level hierarchical meta-analytic model explicitly models three sources of variance:

- **Level 1 (sampling variance)**: variation in effect sizes within a given experiment due to finite sample size in each study.
- **Level 2 (within-paper variance)**: heterogeneity among effect sizes reported by the same paper (different experiments within a paper differ from each other).
- **Level 3 (between-paper variance)**: heterogeneity across papers (systematic differences between research groups, tasks, populations).

Model is estimated via Restricted Maximum Likelihood (REML). Effect sizes are weighted by the inverse of their Level-1 sampling variance. The overall pooled estimate and its confidence interval account for all three levels simultaneously.

## Procedure

1. Compute Hedges' g for each effect size from raw statistics (means, SDs, sample sizes) or from reported statistics (t, F, p).
2. Organize effect sizes into a nested structure: effect sizes → experiments → papers.
3. Fit the three-level REML model using metafor or equivalent software.
4. Report pooled effect, confidence interval, and I² decomposed across levels.
5. Extend to meta-regression by adding moderator predictors (categorical or continuous) and testing F-statistics for subgroup differences.

## Assumptions

- Effect sizes within each level are exchangeable conditional on the level above.
- Sampling variances are correctly estimated from the reported statistics.
- No severe publication bias (tested separately with funnel plots / Egger's test).

## Limitations

- Does not account for measurement-error variation across studies (e.g., some studies use 500 test items, others use 15).
- Cannot directly model interaction effects between moderators without very large corpora.
- Requires sufficient papers for stable Level-3 variance estimation (rule of thumb: ≥10 papers).

## Tradeoff profile

- More correct than standard random-effects meta-analysis when data are nested.
- More computationally intensive and harder to interpret for non-statisticians.
- Robust to modest violations of the normality of random effects.

## Evaluated by

- [[when-combinations-humans-ai-useful-systematic]] — applied to 370 effect sizes from 106 experiments across 74 papers on human–AI collaboration.

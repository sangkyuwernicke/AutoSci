---
name: "Three-Level Meta-Analytic Model"
slug: three-level-meta-analytic-model
type: evaluation
tags:
  - meta-analysis
  - statistics
  - effect size
  - systematic review
source_papers:
  - "[[when-combinations-humans-ai-useful]]"
parent_methods: []
child_methods: []
realizes_concepts:
  - "[[human-ai-synergy]]"
  - "[[human-augmentation]]"
date_updated: 2026-05-29
---

## Problem setting

Standard meta-analytic models assume effect sizes are independent — one effect size per study. In practice, experiments often generate multiple dependent effect sizes: multiple treatment conditions vs. a single control, or multiple performance metrics on the same participants. Nested data structures (effect sizes within experiments within papers) violate independence and produce biased variance estimates.

## Mechanism

A three-level random-effects model explicitly accounts for three sources of variance:
1. **Level 1 (within-study sampling variance):** Variance attributable to sampling error within a single effect size estimate.
2. **Level 2 (within-experiment variance):** Variance among effect sizes from the same experiment (due to multiple conditions or measures).
3. **Level 3 (between-experiment variance):** Variance in true effects across experiments.

**Robust variance estimation (RVE)** with the Knapp-Hartung adjustment is layered on top to produce consistent standard errors, confidence intervals, and test statistics even when effect size sampling errors are correlated (e.g., multiple treatment arms vs. a shared control).

**Moderator analysis** is performed as meta-regression on the three-level model, with F-tests comparing subgroup effect sizes.

## Procedure

1. Calculate Hedges' g for each effect size (standardized mean difference, corrected for small-sample bias).
2. Fit the three-level random-effects model (implemented in R `metafor`, function `rma.mv`).
3. Apply RVE to compute cluster-robust SEs, with experiments as clusters.
4. Compute I² at each level (following Cheung 2014) to attribute heterogeneity to within- vs. between-experiment sources.
5. Run separate meta-regressions for each moderator variable.
6. Perform funnel plot + Egger's regression + rank correlation test for publication bias.

## Assumptions

- Experiments are independent (no shared participants across experiments in different papers).
- The effect size distribution has a random component at each level (not fixed effects).
- Clustering at experiment level for RVE; participants only overlap within an experiment.

## Limitations

- Does not account for potential interaction effects between moderators (requires large N).
- Clustering at experiment level rather than paper level is an assumption; paper-level sensitivity analysis is recommended.
- I² interpretation can be ambiguous in multilevel models.

## Tradeoff profile

Appropriate when: studies generate multiple dependent effect sizes, large N of effect sizes, interest in both average effect and moderators.
Less appropriate when: effect sizes are fully independent (standard two-level model suffices) or N is very small.

## Evaluated by

Used in [[when-combinations-humans-ai-useful]] to synthesize 370 effect sizes across 106 experiments.

---
title: "Human Augmentation"
aliases:
  - AI-assisted human performance
  - human-AI augmentation
  - human enhancement via AI
tags:
  - human-ai-collaboration
  - performance-evaluation
  - ai-augmentation
maturity: active
definition: "The condition in which a human–AI combined system outperforms the human working alone, regardless of how the AI alone performs."
key_papers:
  - "[[when-combinations-humans-ai-useful-systematic]]"
first_introduced: "2024"
date_updated: 2026-05-28
related_concepts:
  - "[[human-ai-synergy]]"
---

## Definition

Human augmentation is achieved when a human–AI combined system produces performance strictly greater than the human working alone: P(H+AI) > P(H). This is a weaker criterion than [[human-ai-synergy]] because it does not require beating the AI alone. Human augmentation is the appropriate standard when full automation is infeasible for legal, ethical, or safety reasons, or when the goal is specifically to enhance human capability rather than to find the most efficient solution.

## Intuition

Even if an AI is far superior to the human, the human may still benefit from AI assistance—the AI effectively raises the human's floor. The meta-analytic finding (Vaccaro et al. 2024) that human augmentation is robustly positive (g = 0.64) while human–AI synergy is negative (g = −0.23) shows that AI reliably helps humans exceed their unaided performance without necessarily exceeding what the AI alone could do.

## Variants

- **Full augmentation / synergy**: combined exceeds both human and AI alone.
- **Partial augmentation**: combined exceeds human alone but not AI alone.
- **No augmentation**: combined fails to exceed even the human alone (rare, but occurs in ~15% of effect sizes in Vaccaro et al. 2024).

## Comparison

Human augmentation is the standard used in most applied human–AI collaboration studies (mandatory human-in-the-loop settings, e.g., clinical decision support, legal review). Human–AI synergy is the standard relevant to system designers who ask whether a combined system is better than the best available alternative.

## Known limitations

- Augmentation can mask situations where deploying AI alone would be far more cost-effective.
- In high-stakes settings (radiology, bail prediction), cost-sensitive metrics may matter more than average accuracy—augmentation should be evaluated on composite metrics.
- Augmentation is less demanding as AI performance improves: a mediocre AI that boosts humans is still augmentation, even though synergy is absent.

## Open problems

- Designing composite performance metrics (error-cost weighting, throughput, fairness) that reveal meaningful augmentation beyond raw accuracy.
- Understanding when augmentation is sufficient justification for human-in-the-loop vs. when synergy should be the design target.

## Relationship to foundations

Related to the ergonomics and cognitive science literature on skill augmentation, and to the human factors tradition of human–automation interaction.

## Realized by

- [[three-level-meta-analytic-model]] — used to estimate pooled augmentation effect sizes in Vaccaro et al. 2024

## My understanding

The robustly large augmentation effect (g = 0.64) in Vaccaro et al. is practically important: AI reliably helps humans, even when it does not produce synergy. The challenge is that most practitioners conflate augmentation with synergy, leading to overconfidence in human–AI systems.

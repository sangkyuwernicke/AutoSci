---
title: "Human Augmentation"
aliases:
  - human augmentation by AI
  - weak human-AI synergy
  - AI-augmented human performance
  - human-AI augmentation
tags:
  - human-AI collaboration
  - performance evaluation
  - AI assistance
maturity: active
definition: "The condition where a human-AI combination outperforms the human working alone, regardless of how it compares to the AI alone — a weaker criterion than human-AI synergy."
key_papers:
  - "[[when-combinations-humans-ai-useful]]"
first_introduced: "Used as a benchmark condition in Vaccaro et al. 2024 (arXiv 2405.06087)"
date_updated: 2026-05-29
related_concepts:
  - "[[human-ai-synergy]]"
---

## Definition

Human augmentation measures whether AI assistance helps humans perform better than they would without it. Formally: performance(human-AI) > performance(human alone). This is a weaker condition than [[human-ai-synergy]] because it does not require the combined system to beat the AI alone.

Human augmentation is the appropriate goal in contexts where full automation is legally, ethically, or practically prohibited — for example, medical decisions requiring physician sign-off or legal judgments requiring human accountability.

## Intuition

Even if an AI system is more accurate than humans alone, adding the human to the loop can still raise performance above the human-alone baseline. This happens because the AI provides relevant information or suggestions that the human can incorporate, even if the human does not always correctly weight the AI's advice. The concern is that using "augmentation" as the sole success criterion masks whether the human is actually adding value relative to just deploying the AI alone.

## Variants

- **Relative augmentation:** Improvement over the human, regardless of AI performance.
- **Absolute performance gain:** Absolute improvement in task metric, independent of baseline.

## Comparison

Vaccaro et al. (2024) found that, on average across 370 effect sizes, human augmentation exists (g = +0.64, p < 0.001) even when human-AI synergy does not (g = -0.23, p = 0.005). This discrepancy is consistent with: the AI providing useful suggestions that lift the human, but the human introducing enough noise that the combined system still falls short of the AI alone.

## Known limitations

- Augmentation is vulnerable to publication bias: studies comparing human-AI to human alone are more likely to show positive results and more likely to be published, inflating average estimates.
- Augmentation does not reflect the opportunity cost of deploying humans when AI alone would suffice.

## Open problems

- In which high-stakes domains does augmentation (keeping humans in the loop) remain valuable even when AI outperforms humans, due to error-cost asymmetries or accountability requirements?

## Relationship to foundations

Related to decision-support systems research and the broader literature on human-computer interaction and cognitive aids.

## Realized by

## My understanding

Human augmentation is the "floor" evaluation that most human-AI studies use. It answers "is the human better off with AI than without?" but not "is the system better off with the human?" For practical deployment decisions the latter question matters more.

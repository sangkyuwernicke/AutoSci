---
title: "Human–AI Synergy"
aliases:
  - human-AI synergy
  - human-AI complementarity
  - strong human-AI complementarity
tags:
  - human-ai-collaboration
  - performance-evaluation
  - collective-intelligence
maturity: active
definition: "The condition in which a human–AI combined system outperforms the better of the human alone and the AI alone on the same task."
key_papers:
  - "[[when-combinations-humans-ai-useful-systematic]]"
first_introduced: "2024"
date_updated: 2026-05-28
related_concepts:
  - "[[human-augmentation]]"
---

## Definition

Human–AI synergy occurs when a combined human–AI system achieves performance *strictly exceeding* the maximum of what either the human alone or the AI alone can achieve. This is analogous to "strong synergy" in human group research: the group outperforms its best member. Contrast with **human augmentation**, where the combined system merely beats the human alone (a weaker criterion that an AI working alone might also satisfy).

Formally: let P(H), P(AI), P(H+AI) be performance on a common metric. Human–AI synergy ⟺ P(H+AI) > max(P(H), P(AI)).

## Intuition

Synergy requires that humans and AI contribute genuinely complementary capabilities—each better at different subtasks—and that the system correctly routes work to the superior partner. It is not guaranteed by AI skill alone; if AI is already better than the human, adding the human can actively hurt because the human may override correct AI outputs with noisier judgements.

## Variants

- **Task-partitioned synergy**: humans and AI explicitly handle different subtasks (division of labour), maximizing complementarity. Rare in practice (only ~3 of 106 experiments in Vaccaro et al. 2024).
- **Human augmentation**: weaker condition; human–AI combined beats the human alone but may fall short of the AI alone.
- **AI augmentation**: combined beats the AI alone but falls short of the human alone (rare in modern AI settings).

## Comparison

| Condition | Baseline | Outcome |
|---|---|---|
| Human–AI synergy | max(human, AI) | combined > max |
| Human augmentation | human alone | combined > human |
| No benefit | human alone | combined ≤ human |

## Known limitations

- Measuring synergy requires eliciting the AI-alone baseline, which many studies omit (they only compare human–AI to human alone, measuring augmentation).
- Task performance is multi-dimensional; synergy on accuracy may coincide with regression on speed or cost.
- Synergy is task-specific: the same human–AI pair may show synergy on creation tasks and losses on decision tasks.

## Open problems

- What collaboration architectures reliably produce synergy even when AI outperforms humans on the task overall?
- How does the synergy landscape shift as AI capabilities improve—will the human-outperforms-AI regime (where synergy is easier) shrink?
- Can commensurability standards for human–AI experiments enable systematic tracking of synergy rates across the literature?

## Relationship to foundations

Conceptually related to complementarity and division of labour in human group research and to the theory of comparative advantage in economics.

## Realized by

- [[three-level-meta-analytic-model]] — the statistical framework used to estimate and test human–AI synergy in meta-analysis

## My understanding

The power of Vaccaro et al. (2024) is showing that average synergy is *negative*, yet highly heterogeneous, and that the task-type and relative-performance moderators are the key levers. Synergy is not a default property of human–AI teams; it must be engineered through deliberate task design and allocation.

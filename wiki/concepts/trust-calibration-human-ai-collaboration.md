---
title: "Trust Calibration in Human-AI Collaboration"
aliases:
  - well-calibrated trust
  - trust miscalibration
  - HAI trust calibration
tags:
  - human-ai-collaboration
  - trust
  - decision-making
  - explainable-ai
maturity: active
definition: "The alignment between a human decision-maker's actual trust in an AI system's recommendation and the recommendation's true quality — neither over-trusting (algorithm appreciation) nor under-trusting (algorithm aversion) the system."
key_papers:
  - "[[optimizing-human-ai-collaboration-effects-motivation]]"
first_introduced: "~2020 (Zerilli et al., Zhang et al.)"
date_updated: 2026-05-29
related_concepts: []
linked_ideas: []
---

## Definition

Trust calibration refers to the degree to which a human's willingness to rely on an AI system's recommendation matches the actual reliability of that recommendation. A well-calibrated user trusts high-quality AI outputs and appropriately discounts low-quality ones. Miscalibration takes two forms: over-trust (algorithm appreciation — uncritically accepting recommendations) and under-trust (algorithm aversion — exaggerated rejection, often after observing a single AI error).

## Intuition

Think of trust calibration as a dial: uncalibrated users lock the dial at one extreme (always trust or never trust), whereas calibrated users adjust the dial recommendation-by-recommendation based on contextual cues about output quality. XAI explanations are meant to supply those cues, but they fail if users process them heuristically rather than systematically.

## Variants

- **Behavioural trust calibration** — measured by deviation of human rating from AI recommendation, stratified by recommendation quality.
- **Self-reported trust calibration** — survey items (e.g. "I perceived the AI as trustworthy"); empirically decoupled from behavioural trust.
- **Dynamic trust trajectories** — how trust evolves across interaction episodes, especially after error detection.

## Comparison

Trust calibration is distinct from raw trust level: two users can have the same mean trust level but differ dramatically in calibration (one always trusts; the other trusts selectively). Standard XAI evaluation conflates these by measuring overall accuracy rather than calibration-sensitive accuracy.

## Known limitations

- Behavioural trust measures (deviation from AI recommendation) conflate trust with disagreement for reasons unrelated to quality assessment.
- Self-reported trust is post-hoc and subject to memory/introspection limits.
- Calibration is task-dependent: a well-calibrated user in one domain may not transfer calibration to another.

## Open problems

- No agreed-upon metric for trust calibration that separates quality-sensitive from quality-insensitive following behaviour.
- Unclear whether calibration can be trained or whether it emerges naturally with AI experience.
- Interaction effects between accuracy cues and domain expertise remain unstudied.

## Relationship to foundations

Grounded in dual process theories of cognition (Chaiken 1980; Strack & Deutsch 2004): systematic processing enables calibration; heuristic processing undermines it.

## Realized by

## My understanding

Trust calibration is the key mediating construct between XAI intervention design and actual HAI performance gains. The Eisbach et al. (2023) study shows that motivation and accuracy information both improve calibration but via different mechanisms — motivation increases correct trust in good recommendations, while accuracy information improves both arms of calibration simultaneously.

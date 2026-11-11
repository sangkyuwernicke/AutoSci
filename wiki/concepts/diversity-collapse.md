---
title: Diversity Collapse
aliases:
  - output homogenization
  - AI-induced homogeneity
  - diversity reduction
tags:
  - AI outputs
  - homogeneity
  - human-AI collaboration
  - creativity
maturity: active
definition: The reduction in output diversity that occurs when AI agents contribute substantially to collaborative or individual creative work, resulting in outputs that are more self-similar across teams or individuals compared to human-only conditions.
key_papers:
  - "[[collaborating-ai-agents-field-experiment-teamwork]]"
first_introduced: Padmakumar & He 2024; Chen et al. 2024
date_updated: 2026-05-29
related_concepts:
  - "[[human-ai-collaboration]]"
  - "[[jagged-frontier]]"
  - "[[delegation-workflow]]"
---

## Definition

Diversity collapse occurs when AI assistance causes the distribution of outputs produced by different people or teams to converge toward the AI's modal output, reducing creative variation across the population. It reflects the tension between the average-quality improvement AI can deliver and the variance reduction that comes with consistent AI contributions.

## Evidence

- Ju & Aral (2025): Human-AI teams produced outputs significantly closer to their condition centroid (cosine distance β=−0.094, p<0.001), indicating homogenization relative to human-human teams.
- Mechanism: Higher delegation to AI reduced output diversity (β=−0.083, p<0.001), while interpersonal communication (more common in human-human teams) predicted higher output diversity, suggesting social exchange facilitates novel idea-sharing.
- Quality-diversity trade-off: HAI teams produced higher average text quality but less diverse outputs; at organizational scale, diversity collapse may reduce the creative variation that enables exploration of new ideas.

## Implications

- Organizations seeking creative variation should design workflows that preserve human-driven ideation (e.g., human-only brainstorming before AI-assisted execution).
- Diversity collapse is a direct downstream consequence of the delegation workflow: as delegation increases, AI's stylistic imprint dominates.

## Related concepts

- [[human-ai-collaboration]] — the collaborative setting in which diversity collapse is observed
- [[delegation-workflow]] — the behavioral mechanism driving diversity collapse
- [[jagged-frontier]] — related quality–capability asymmetry in AI collaboration

## Recent work

- [[collaborating-ai-agents-field-experiment-teamwork]] — first experimental documentation of diversity collapse in an agentic, dyadic human-AI collaboration setting with mechanism tracing to delegation behavior.

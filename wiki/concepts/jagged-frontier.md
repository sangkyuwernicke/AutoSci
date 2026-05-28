---
title: Jagged Frontier
aliases:
  - AI capability frontier
  - jagged frontier of AI
tags:
  - AI capabilities
  - human-AI collaboration
  - task performance
  - AI limitations
maturity: active
definition: The uneven profile of AI performance across task types, where AI systems excel on some dimensions (e.g., text generation, structured reasoning) while underperforming on others (e.g., image quality judgment, open-ended visual creativity), creating a frontier that is not uniformly advanced or receding.
key_papers:
  - "[[collaborating-ai-agents-field-experiment-teamwork]]"
first_introduced: "Dell'Acqua et al. 2023 (Navigating the Jagged Technological Frontier)"
date_updated: 2026-05-29
related_concepts:
  - "[[human-ai-collaboration]]"
  - "[[diversity-collapse]]"
---

## Definition

The jagged frontier describes the irregular boundary of AI capability: for any given AI system, some tasks fall inside the frontier (AI performs well) while others fall outside it (AI performs poorly or inconsistently), and this boundary does not correspond neatly to naive notions of task difficulty. The concept implies that task-level allocation decisions—not just AI versus no AI—are critical for capturing AI's benefits while managing its limitations.

## Evidence

- In ad-creation experiments (Ju & Aral 2025), LLM-based agents improved text quality (inside frontier) but reduced image quality (outside frontier) relative to human-human teams.
- These quality differences mapped to distinct field performance effects: text quality → higher CTR and longer VTD; image quality → lower CPC.
- The jagged frontier extends beyond output quality to downstream business metrics, with AI's comparative advantages creating heterogeneous performance profiles across outcome dimensions.

## Related concepts

- [[human-ai-collaboration]] — the setting in which the jagged frontier is most often studied
- [[diversity-collapse]] — co-occurring phenomenon in human-AI teaming

## Recent work

- [[collaborating-ai-agents-field-experiment-teamwork]] — empirical documentation in agentic, multimodal ad-creation task with field experiment validation.

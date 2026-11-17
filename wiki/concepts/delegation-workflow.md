---
title: Delegation Workflow
aliases:
  - AI delegation pattern
  - directive collaboration
tags:
  - human-AI collaboration
  - delegation
  - teamwork
  - work processes
maturity: emerging
definition: A collaboration pattern observed in human-AI teams where humans shift from direct task execution to directing and delegating work to AI partners via task-oriented communication, resulting in higher productivity on AI-strength tasks at the cost of reduced output diversity.
key_papers:
  - "[[collaborating-ai-agents-field-experiment-teamwork]]"
first_introduced: "Ju & Aral 2025"
date_updated: 2026-05-29
related_concepts:
  - "[[human-ai-collaboration]]"
  - "[[diversity-collapse]]"
  - "[[jagged-frontier]]"
---

## Definition

The delegation workflow describes how human behavior in human-AI teams organizes around direction and oversight rather than direct execution. Humans communicate more frequently and with greater task focus (content, process, instruction messages), perform fewer manual edits, and delegate more of the actual work to the AI agent. This workflow is amplified when participants correctly recognize their partner as AI (recognition), enabling behavioral adaptation away from social maintenance toward task direction.

## Mechanism

The delegation workflow unfolds through three linked behaviors:
1. **Task-oriented communication** — more content/process messages (suggestions, instructions, planning), fewer social/emotional messages
2. **Delegation** — higher fraction of work performed by the AI partner (62% fewer direct edits; 17% more task delegation)
3. **Recognition** — correct identification of AI partner amplifies both task-orientation and delegation, improving output quality

Together, these behaviors explain the productivity gains, jagged-frontier quality profile, and diversity collapse observed in human-AI teaming.

## Consequences

- Improves text quality (AI strength) and productivity
- Does not improve image quality (AI weakness) — consistent with the jagged frontier
- Reduces output diversity (diversity collapse) as AI's contributions dominate

## Related concepts

- [[human-ai-collaboration]] — the broader setting in which delegation workflows emerge
- [[jagged-frontier]] — the capability constraint that shapes which delegated tasks benefit
- [[diversity-collapse]] — downstream consequence of high delegation

## Recent work

- [[collaborating-ai-agents-field-experiment-teamwork]] — empirical identification and mechanism tracing of the delegation workflow in a randomized field experiment.

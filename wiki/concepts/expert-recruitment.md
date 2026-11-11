---
title: "Expert Recruitment"
aliases:
  - dynamic agent composition
  - dynamic role assignment
  - dynamic team formation
tags:
  - multi-agent-systems
  - llm-agents
  - collaboration
  - role-assignment
maturity: emerging
definition: "A mechanism in multi-agent LLM systems where a designated recruiter agent dynamically generates role descriptions and assembles a group of specialized expert agents tailored to a specific goal and current problem-solving state, adjusting group composition across rounds based on evaluator feedback."
key_papers:
  - "[[agentverse-facilitating-multi-agent-collaboration-exploring]]"
first_introduced: "Introduced as a formal stage in AgentVerse (Chen et al., 2023; arXiv:2308.10848)."
date_updated: 2026-05-29
related_concepts:
  - "[[multi-agent-collaboration]]"
---

## Definition

Expert recruitment is the process of dynamically forming and adapting a group of specialized agents for a given task. Unlike static role assignment — where agent roles are pre-defined before problem-solving begins — expert recruitment allows a recruiter agent to generate context-appropriate role descriptions on the fly, and to adjust group composition in subsequent rounds based on evaluator feedback. This makes the multi-agent system adaptive to evolving task requirements.

## Key properties

- **Dynamic composition**: Group membership changes each round based on progress and feedback, not fixed at initialization.
- **Recruiter role**: A dedicated agent (analogous to a human resource manager) generates expert descriptions from the goal specification.
- **Feedback-driven adaptation**: If the current group fails to meet the goal, the evaluator's verbal feedback informs the next round's recruitment decision.
- **Scalability**: Avoids requiring manual pre-specification of roles for every possible task type.

## Key papers

- [[agentverse-facilitating-multi-agent-collaboration-exploring]] — introduces expert recruitment as Stage 1 of the AgentVerse framework; demonstrates that dynamic composition improves over static single-agent baselines.

## Realized by

- [[agentverse-framework]]

---
title: "Information Asymmetry in Multi-Agent Systems"
aliases:
  - information asymmetry
  - agent information asymmetry
  - private information in MAS
tags:
  - multi-agent-systems
  - information-asymmetry
  - llm-agents
maturity: emerging
definition: "The condition in which different agents within a system can access only their respective users' private information, preventing any single agent from having a complete view of the data needed for collaborative task resolution."
key_papers:
  - "[[autonomous-agents-collaborative-task-under-information]]"
first_introduced: "2024"
date_updated: 2026-05-29
related_concepts: []
---

## Definition

In a multi-agent system operating under information asymmetry, each agent Ai holds a disjoint private information partition Ii. No agent has access to another agent's partition by default. Tasks that require reasoning over the union R = R1 ∪ R2 ∪ ... ∪ Rn therefore cannot be solved by any single agent alone—they require explicit information exchange among agents.

Formally (following iAgents notation): a task Q is answered by Reasoning(Q, R) where R = R1 ∪ R2, but R1 and R2 are distributed across agents A1 and A2 who can only read their respective information I1 and I2. Communication C(I1, I2, A1, A2) must produce R1 and R2.

## Intuition

Previous LLM-MAS designs (ChatDev, MetaGPT, AgentVerse) assume all agents share a common context—a virtual company with a shared workspace. This is fine for single-user tasks but breaks for multi-person real-world tasks. When Alice and Bob each have private calendars, chat histories, or documents, their agents cannot pool everything into one context without violating privacy or exceeding context limits. Information asymmetry forces agents to reason about *what they don't know*, ask for it explicitly, and verify the received information.

## Variants

- **Environment asymmetry**: agents observe different environmental states (e.g., partial observability in games).
- **Goal asymmetry**: agents have private objectives that may conflict.
- **Mind-state asymmetry**: agents hold different beliefs or mental models.
- **Information asymmetry (data)**: agents can access only their human user's private data—the type studied by iAgents.

## Comparison

Classical multi-agent research (game theory, mechanism design) has long studied information asymmetry in the economic sense. In LLM-MAS, the challenge is distinctly *operational*: LLMs cannot memorize all user-specific knowledge at pre-training time, and dynamic personal data is too large and private to aggregate.

## Known limitations

- Resolving asymmetry via information exchange is fundamentally in tension with privacy—the more agents share, the better the task performance, but the higher the privacy cost.
- LLM hallucination can produce "fake solved" states where an agent incorrectly marks a rationale as known.

## Open problems

- Formal privacy bounds on information exchange in agent networks.
- Mechanism design for selectively sharing only task-relevant information fragments.
- Scalability beyond two-agent settings to networks of hundreds of users.

## Relationship to foundations

Relates to partial-observability in MDPs and mechanism design under incomplete information in classical economics.

## Realized by

- [[infonav]] — InfoNav addresses information asymmetry by explicit plan-and-track reasoning
- [[informative-multi-agent-system]] — iAgents is the system instantiating this concept

## My understanding

The key insight is that information asymmetry in LLM-MAS is not just a technical challenge but a design requirement for privacy-preserving multi-person AI assistants. The iAgents paper is the first to name and benchmark this problem in the context of communicative LLM agents.

---
title: "Multi-Agent Collaboration"
aliases:
  - multi-agent system
  - MAS
  - agent cooperation
  - multi-agent cooperation
tags:
  - multi-agent-systems
  - llm-agents
  - collaboration
  - autonomous-agents
maturity: active
definition: "A paradigm in which multiple autonomous agents work together — sharing information, distributing subtasks, and collectively making decisions — to accomplish goals that are difficult or impossible for a single agent to achieve alone. In LLM-based systems, collaboration is typically structured through communication protocols (horizontal or vertical), role assignment, and shared evaluation."
key_papers:
  - "[[agentverse-facilitating-multi-agent-collaboration-exploring]]"
first_introduced: "Multi-agent systems research predates LLMs; LLM-based collaborative agents emerged prominently in 2023."
date_updated: 2026-05-29
related_concepts:
  - "[[expert-recruitment]]"
  - "[[emergent-agent-behaviors]]"
---

## Definition

Multi-agent collaboration refers to structured cooperation among multiple autonomous agents to jointly solve complex tasks. Each agent may have a distinct role, capability, or knowledge domain, and agents communicate to synthesize a collective decision or action. In LLM-based settings, collaboration emerges from prompt-driven role assignment and iterative discussion protocols.

## Key properties

- **Role diversity**: Agents are assigned or self-assign distinct roles (solver, reviewer, recruiter) that partition the problem space.
- **Communication structure**: Collaboration is organized via horizontal (democratic, all-agents) or vertical (hierarchical, solver + reviewers) communication topologies.
- **Iterative refinement**: Multi-round deliberation allows agents to correct each other's errors and converge on higher-quality outputs.
- **Emergent behaviors**: Interaction among agents can produce unplanned behaviors — both beneficial (volunteer, conformity) and harmful (destructive).

## Key papers

- [[agentverse-facilitating-multi-agent-collaboration-exploring]] — proposes AgentVerse as a general multi-agent framework with dynamic composition and structured deliberation; demonstrates emergent collaborative behaviors.

## Realized by

- [[agentverse-framework]]

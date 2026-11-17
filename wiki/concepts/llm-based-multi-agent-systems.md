---
title: "LLM-based Multi-Agent Systems"
aliases:
  - LLM-MA
  - multi-agent LLM systems
  - LLM multi-agents
tags:
  - multi-agent-systems
  - llm-agents
  - collective-intelligence
  - agent-collaboration
maturity: active
definition: "Systems in which multiple autonomous agents, each powered by a large language model, collaborate through structured communication to solve complex tasks or simulate real-world phenomena by leveraging specialized roles and collective intelligence."
key_papers:
  - "[[large-language-model-based-multi-agents]]"
first_introduced: "2023"
date_updated: 2026-05-29
related_concepts:
  - "[[agent-communication]]"
  - "[[agent-capability-acquisition]]"
---

## Definition

An LLM-based Multi-Agent System (LLM-MA) consists of two or more autonomous agents each driven by a large language model. Each agent has a distinct profile (role, capabilities, constraints) and communicates with other agents — and potentially with external environments — using natural language. The system's power derives from collective intelligence: agents specialize, debate, cooperate, and coordinate to tackle tasks that exceed the scope of any single agent.

## Intuition

Think of a software development team: a product manager, an engineer, and a tester each bring specialized expertise, and the group produces better software than any one member could alone. LLM-MA formalizes this insight: instead of prompting a single LLM to wear all hats, assign each hat to a separate LLM-powered agent with a focused role prompt. Communication between agents replaces internal chain-of-thought.

## Variants

- **Problem-solving systems**: agents cooperate to produce a concrete output (code, scientific results, answers). Communication is typically cooperative or layered.
- **World simulation systems**: agents enact roles in a simulated environment (social, game, policy) to study emergent behavior. Communication is more peer-to-peer and competitive.
- **Hybrid frameworks**: systems like AutoGen and MetaGPT support both modes via configurable agent graphs.

## Comparison

| Aspect | Single LLM Agent | LLM-MA System |
|---|---|---|
| Specialization | One agent juggles all roles | Each agent has a dedicated role |
| Parallelism | Sequential | Parallel task execution possible |
| Communication | Internal CoT | Explicit inter-agent messages |
| Scalability | Limited by context window | Distributed context across agents |
| Coordination cost | None | Requires orchestration design |

## Known limitations

- Hallucinations can cascade: one agent's error propagates to others.
- Communication overhead grows super-linearly with number of agents.
- Collective intelligence does not automatically emerge from agent count; orchestration design matters.
- Most current systems are text-only; multi-modal settings remain largely unexplored.

## Open problems

- Optimal agent orchestration strategies for task-agent assignment.
- Scaling laws: how does collective performance scale with agent count?
- Benchmark standardization for world simulation tasks.

## Relationship to foundations

Draws from classical multi-agent systems theory, collective intelligence research, and role theory from sociology. Enabled by the planning/reasoning capabilities of modern LLMs.

## Realized by

- MetaGPT (SOP-embedded agent framework)
- CAMEL (inception-prompting cooperative framework)
- AutoGen (customizable multi-agent conversation framework)

## My understanding

The key insight of LLM-MA over single-agent prompting is the separation of concerns at inference time: rather than one model handling all sub-tasks, each sub-task is handled by a model conditioned on a specialized role. The communication channel between agents becomes an explicit coordination mechanism that can be designed, debugged, and optimized.

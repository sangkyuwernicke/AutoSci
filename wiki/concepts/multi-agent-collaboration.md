---
title: Multi-Agent Collaboration
aliases:
  - MAC
  - multi-agent systems
  - MAS
  - multi-agent LLM systems
tags:
  - multi-agent-systems
  - llm-agents
  - agent-coordination
maturity: active
definition: A paradigm in which multiple LLM-powered agents with distinct specializations communicate and coordinate to solve complex tasks that exceed the capability of any single agent.
key_papers:
  - "[[towards-effective-genai-multi-agent-collaboration]]"
first_introduced: "1980s (classical MAS); LLM-era resurgence circa 2023"
date_updated: 2026-05-28
related_concepts: []
linked_ideas: []
---

## Definition

Multi-agent collaboration (MAC) refers to systems where multiple autonomous AI agents—each with specialized roles, tools, and instructions—communicate via defined protocols to jointly accomplish a goal. In the LLM era, agents are powered by large language models and use function-calling or prompting to interact. The "collaborative assumption" holds that agents are motivated to achieve shared or compatible goals rather than competing individually.

## Intuition

A single LLM agent has a limited context window and must manage many competing instructions simultaneously, leading to hallucinations and tool-call errors on complex tasks. By decomposing the task space and assigning each agent a focused specialty, MAC systems can maintain higher reliability, reduce per-agent instruction overload, and parallelize sub-tasks. The supervisor agent handles orchestration; specialist agents handle execution within their domain.

## Variants

- **Centralized hierarchy (hierarchical agents)**: A root supervisor agent delegates to leaf specialists in a tree topology. The supervisor is responsible for planning, task assignment, and aggregation. Specialists focus on narrow sub-tasks. (This is the design studied in [[towards-effective-genai-multi-agent-collaboration]].)
- **Decentralized hierarchy**: Agents self-organize without a central authority (e.g., MAD, Generative Agents).
- **Sequential workflow**: Each agent processes output from the previous agent in a pipeline (e.g., CrewAI, LangGraph).
- **Peer-to-peer collaboration**: Agents negotiate directly (e.g., CAMEL inception prompting).

## Comparison

| Property | Centralized MAC | Decentralized MAC | Single Agent |
|---|---|---|---|
| Task decomposition | Supervisor | Self-organized | Monolithic |
| Specialization | High | Medium | Low |
| Orchestration overhead | Medium | Low | None |
| Fault isolation | Good | Variable | Poor |

## Known limitations

- Orchestration latency accumulates with each inter-agent round trip.
- Supervisor agent can become a bottleneck and hallucinate routing decisions.
- Multi-agent evaluation is harder than single-agent evaluation due to combinatorially many valid trajectories.
- Context management across long multi-party conversations remains challenging.

## Open problems

- How to automatically select the optimal team size and hierarchy depth for a given task.
- Asynchronous communication protocols that allow agents to proceed without blocking.
- Formal methods for verifying agent coordination correctness.

## Relationship to foundations

Draws on classical distributed systems (message passing, fault tolerance), game theory (mechanism design, coordination), and cognitive science (team cognition, division of labor).

## Realized by

- [[assertion-based-benchmarking]] — evaluation methodology for MAC systems
- [[dynamic-agent-routing]] — optimization technique for reducing MAC orchestration overhead

## My understanding

MAC is the central architectural paradigm of the AWS Bedrock multi-agent framework evaluated in [[towards-effective-genai-multi-agent-collaboration]]. The empirical result that MAC achieves up to 70% relative improvement over single-agent baselines in Software Development validates the specialization hypothesis.

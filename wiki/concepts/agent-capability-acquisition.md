---
title: "Agent Capability Acquisition"
aliases:
  - agent learning
  - agent adaptation
  - multi-agent capability growth
tags:
  - multi-agent-systems
  - llm-agents
  - agent-learning
  - self-evolution
maturity: active
definition: "The mechanisms through which agents in a multi-agent LLM system improve their capabilities over time via feedback from the environment, other agents, or humans, using memory, self-evolution, or dynamic agent generation."
key_papers:
  - "[[large-language-model-based-multi-agents]]"
first_introduced: "2023"
date_updated: 2026-05-29
related_concepts:
  - "[[llm-based-multi-agent-systems]]"
  - "[[agent-communication]]"
---

## Definition

Agent capability acquisition covers how individual agents — and the multi-agent system as a whole — develop and improve their problem-solving abilities during or between interactions. It is defined along two axes: (1) the **feedback source** from which agents learn, and (2) the **adjustment strategy** agents use to update themselves.

## Intuition

A skilled team does not just execute tasks — it learns from experience. Agents in LLM-MA systems face the same challenge: how to retain useful information, generalize from past successes, and adapt when strategies fail. Unlike traditional multi-agent RL, LLM-MA agents acquire capabilities primarily through in-context mechanisms rather than gradient-based updates.

## Variants

**Feedback Sources**:
- **Environment feedback**: code interpreter results, simulator outputs, physical environment observations.
- **Agent interaction feedback**: critiques from other agents, debate outcomes, inter-agent communication logs.
- **Human feedback**: explicit correction signals, preferences, value alignment inputs (human-in-the-loop).
- **None**: world simulation studies that focus on emergent behavior analysis without training agents.

**Adjustment Strategies**:
- **Memory**: agents store interaction history in short-term (context window) or long-term (vector database) memory and retrieve relevant past successes when facing similar situations.
- **Self-evolution**: agents modify their own goals, planning strategies, or behavior based on feedback. Includes fine-tuning on communication logs (Learning through Communication, LTC paradigm). Goes beyond simple history retrieval to genuine profile/strategy updating.
- **Dynamic generation**: new agents are created on-the-fly during task execution to address unforeseen sub-problems. Allows system to scale task-specifically without upfront role enumeration.

## Comparison

| Strategy | Learning signal | Update scope | Cost |
|---|---|---|---|
| Memory | Any feedback | Behavior | Low (retrieval only) |
| Self-evolution | Communication logs / env | Profile + goals | Medium (may require fine-tuning) |
| Dynamic generation | Task structure | Agent population | High (new agent init) |

## Known limitations

- Memory-based approaches do not update the underlying model; they may retrieve irrelevant memories under distribution shift.
- Self-evolution via fine-tuning risks overfitting to narrow communication patterns.
- Dynamic generation increases inference cost and coordination complexity.
- Collective intelligence does not automatically emerge — agents adjusting individually can miss synergies from coordinated multi-agent learning.

## Open problems

- How to jointly optimize multiple agents' strategies rather than adjusting each in isolation.
- How to design reliable interactive environments for continuous LLM-MA learning.
- How to evaluate collective intelligence growth versus individual agent improvement.

## Relationship to foundations

Related to multi-agent reinforcement learning (MARL) but distinct: MARL agents learn via reward signals and gradient updates over many episodes; LLM-MA agents acquire capabilities primarily through in-context learning, retrieval, and occasional fine-tuning on interaction data.

## Realized by

## My understanding

The self-evolution direction — especially the Learning through Communication paradigm — is the most underexplored and potentially highest-impact research direction in this space. If agents can learn from the content of their own inter-agent conversations, this breaks the dependence on curated external training data and creates a self-improving feedback loop.

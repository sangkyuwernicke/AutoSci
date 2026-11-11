---
title: "Informative Multi-Agent System (iAgents)"
aliases:
  - iAgents
  - informative MAS
tags:
  - multi-agent-systems
  - llm-agents
  - information-asymmetry
  - social-networks
maturity: emerging
definition: "A multi-agent paradigm in which the human social network is mirrored as an agent network, and agents proactively exchange private human information to resolve collaborative tasks under information asymmetry."
key_papers:
  - "[[autonomous-agents-collaborative-task-under-information]]"
first_introduced: "2024"
date_updated: 2026-05-29
related_concepts:
  - "[[information-asymmetry-multi-agent-systems]]"
---

## Definition

In iAgents, each human in a social network is assigned a dedicated personal agent. Agents serve *within* the social network (not as a single virtual entity), meaning each agent can only see its own human's private information. When a task requires multi-user collaboration, the relevant agents communicate autonomously and exchange only the information necessary for the task. The framework uses two core mechanisms: InfoNav (for navigation-oriented reasoning) and Mixed Memory (for accurate, comprehensive information retrieval).

## Intuition

Previous MAS designs create a virtual company where all agents share one workspace. iAgents instead creates a digital twin of a real human social network. The topology of agent communication mirrors real-world social connections. This is more privacy-respecting and more scalable: information stays local unless needed for a specific task.

## Variants

- **L1 privacy mode**: agents share all user information freely—maximum efficiency.
- **L2 privacy mode**: agents keep personal information private; edge-side SLM handles local retrieval.
- **L3 privacy mode**: all communication and information processing is local on private devices—still a research challenge.

## Comparison

| System | Information model | Privacy | Scalability |
|---|---|---|---|
| ChatDev / MetaGPT | Shared workspace | None | Single virtual entity |
| Generative Agents | Shared simulated world | None | Town-level simulation |
| iAgents | Per-user private store | Partial (L1–L3) | Social network (140+ users tested) |

## Known limitations

- Privacy–performance trade-off is not resolved; stricter privacy modes reduce accuracy.
- Agent communication costs scale with network size and number of communication turns (~30k tokens/task).
- Human-in-the-loop verification is not yet integrated.

## Open problems

- Lightweight local models for L2/L3 privacy modes.
- Dynamic trust modeling across the agent social network.
- Efficient protocol for selectively disclosing only task-relevant information fragments.

## Relationship to foundations

Connects to distributed cognition (each agent holds a cognitive shard), social network theory (topology guides agent connectivity), and mechanism design (agents decide what to share).

## Realized by

- [[infonav]] — the reasoning and communication navigation mechanism within iAgents

## My understanding

iAgents represents a paradigm shift from "agents as employees of a virtual company" to "agents as personal AI assistants within a real social network." The framework is promising but the privacy architecture is immature—the L2/L3 modes are listed as future work.

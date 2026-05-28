---
title: "Agent Communication"
aliases:
  - inter-agent communication
  - multi-agent communication
  - agent communication paradigms
tags:
  - multi-agent-systems
  - llm-agents
  - communication-structure
maturity: active
definition: "The mechanisms, structures, and content by which agents in a multi-agent system exchange information to coordinate behavior, share knowledge, and reach collective decisions."
key_papers:
  - "[[large-language-model-based-multi-agents]]"
first_introduced: "2023"
date_updated: 2026-05-29
related_concepts:
  - "[[llm-based-multi-agent-systems]]"
  - "[[agent-capability-acquisition]]"
---

## Definition

Agent communication encompasses the full design space for how agents in a multi-agent system exchange messages. It includes three orthogonal dimensions: (1) **Communication Paradigm** — the adversarial/cooperative stance agents take toward each other; (2) **Communication Structure** — the topology of the message graph; and (3) **Communication Content** — what information is exchanged.

## Intuition

Just as human teams have different meeting formats (brainstorming, debate, hierarchical reporting), LLM agents need structured protocols. The choice of communication structure determines what information each agent sees, when, and in what order — directly affecting task quality and efficiency.

## Variants

**Communication Paradigms**:
- **Cooperative**: agents share information toward a common goal (most problem-solving tasks).
- **Debate**: agents argue opposing positions to converge on a better answer (science debate, factuality improvement tasks).
- **Competitive**: agents pursue conflicting objectives (game simulations, market simulations).

**Communication Structures**:
- **Layered/Hierarchical**: agents at each tier have distinct roles; information flows up/down the hierarchy. Used in MetaGPT (SOP-driven waterfall).
- **Decentralized (peer-to-peer)**: agents communicate directly with any other. Common in world simulation.
- **Centralized**: a coordinator node routes all messages. Efficient but creates a bottleneck.
- **Shared Message Pool**: agents publish/subscribe to a shared pool (MetaGPT). Improves communication efficiency by eliminating redundant direct messages.

## Comparison

| Structure | Coordination overhead | Information sharing | Use case |
|---|---|---|---|
| Hierarchical | Low per-agent | Restricted to hierarchy | Software dev (SOPs) |
| Decentralized | High (O(n²)) | Full | World simulation |
| Centralized | Medium | Coordinator-mediated | Task delegation |
| Shared pool | Low | Broadcast | Complex software projects |

## Known limitations

- Debate paradigm can lead to agents reinforcing errors rather than correcting them if the majority is wrong.
- Decentralized peer-to-peer communication does not scale well beyond ~10 agents.
- Communication content in current systems is almost exclusively text; richer modalities (code artifacts, structured data) require special handling.

## Open problems

- How to design communication constraints that prevent hallucination propagation.
- Optimal message compression and routing for large-scale systems.
- Measuring communication quality as distinct from task performance.

## Relationship to foundations

Builds on distributed systems communication theory and speech-act theory (Austin/Searle). In LLM contexts, communication is implemented as natural language prompts, inheriting all the ambiguity and expressiveness of language.

## Realized by

## My understanding

The shared message pool concept from MetaGPT is the most practically impactful communication innovation in recent LLM-MA work. It breaks the O(n²) direct-messaging bottleneck that plagues decentralized designs while preserving full information sharing — a structural improvement that deserves wider adoption.

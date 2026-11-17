---
title: "Multi-Agent System Topology"
aliases: [MAS topology, agent communication topology, inter-agent topology, topological structure MAS]
tags: [multi-agent-systems, graph-learning, topology, agent-coordination, llm-agents]
maturity: emerging
definition: >
  The structural configuration of how agents in a Multi-Agent System (MAS) are configured, connected, and coordinated—formally a directed graph G = (A, E) where nodes are agents and edges are communication links. Topology determines information flow, task decomposition patterns, communication cost, robustness to failures, and fairness of agent participation. Common archetypes include chains, stars, trees, rings, and fully-connected graphs, each suited to different task coordination patterns.
key_papers:
  - "[[topological-structure-learning-should-research-priority]]"
first_introduced: "2025"
date_updated: 2026-05-29
related_concepts: []
linked_ideas: []
---

## Definition

Multi-Agent System (MAS) topology refers to the structural organization of agents and their communication links, modeled as a directed graph $\mathcal{G} = (\mathcal{A}, \mathcal{E})$ where $\mathcal{A}$ is the set of agents and $\mathcal{E} \subseteq \mathcal{A} \times \mathcal{A}$ represents directed communication edges. The topology determines:

- **Information flow**: which agents receive outputs from which agents
- **Task decomposition**: how work is divided and aggregated
- **Communication cost**: token consumption, latency, and API costs
- **Robustness**: resilience to agent failure or adversarial perturbations
- **Fairness**: equitable participation and exposure of different agent roles

## Common Archetypes

| Topology | Structure | Best for |
|---|---|---|
| Chain | Sequential pipeline | Software development, step-by-step refinement |
| Star | Central coordinator | Tool routing, centralized control |
| Tree | Hierarchical | Planning, hierarchical reasoning |
| Ring | Circular | Peer review cycles |
| Fully-connected | All-pairs | High-bandwidth ideation, maximum information sharing |

## Realized by

- [[three-stage-topological-structure-optimization-framework]]

## Key papers

- [[topological-structure-learning-should-research-priority]] — position paper advocating topology-aware MAS design with a three-stage learning framework

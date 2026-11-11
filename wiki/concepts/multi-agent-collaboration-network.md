---
title: "Multi-Agent Collaboration Network"
aliases:
  - MacNet
  - DAG agent network
  - directed acyclic graph multi-agent system
tags:
  - multi-agent-systems
  - llm-agents
  - graph-topology
  - collaborative-ai
maturity: emerging
definition: "A framework for organizing LLM agents into a directed acyclic graph (DAG) topology where node-agents act as producers (actors) and edge-agents act as instructors (critics), enabling scalable multi-agent collaboration with linear context growth."
key_papers:
  - "[[scaling-large-language-model-based-multi]]"
first_introduced: "2024"
date_updated: "2026-05-29"
related_concepts:
  - "[[collaborative-scaling-law]]"
---

## Definition

A Multi-Agent Collaboration Network (MacNet) is a DAG G=(V,E) where each node vᵢ hosts an actor LLM agent that produces task artifacts, and each directed edge ⟨vᵢ,vⱼ⟩ hosts a critic LLM agent that issues instructions. Agents interact in topological order, with only the final refined artifact (not full dialogue) propagated to downstream agents. This bipartite role structure and artifact-only memory control enable the network to scale to thousands of agents while keeping context consumption O(n) rather than O(n²).

## Intuition

Inspired by social network theory: information propagates through directed edges, acyclicity prevents backflow, and the bipartition of labor (critics direct, actors produce) mirrors organizational hierarchies. The topological ordering ensures each agent has all prerequisite context before acting, without global broadcasting.

## Variants

- **Chain**: Linear sequence; sequential artifact refinement; best for procedural tasks (e.g., software development).
- **Star**: One central node distributes to many leaves; parallel aspect exploration; good for creative tasks.
- **Tree**: Hierarchical branching; intermediate between chain and star; wider = better than deeper due to memory control.
- **Mesh (fully-connected)**: Maximum interaction density; highest quality but high cost and context pressure.
- **Layer (MLP-shaped)**: Layered structure balanced in width and depth; intermediate density.
- **Random**: Edges randomly pruned from mesh while maintaining connectivity; exhibits small-world properties (short average path length + high clustering); best average quality at 51.92% less time than mesh.

## Comparison

MacNet vs. baseline multi-agent frameworks:
- vs. **Majority voting**: Independent agents, no interdependence; plateaus at ~8 agents with only 0.9% gain.
- vs. **AgentVerse**: Hierarchical but context explosion beyond 30 agents; fixed topology.
- vs. **GPTSwarm**: Optimized graph with custom node/edge functions; requires per-task manual setup; not general.
- vs. **Chain-of-Thought (single agent)**: No collaborative refinement; MacNet-Chain surpasses CoT on most tasks through iterative critic-actor refinement.

## Known limitations

- Artifact-only memory propagation can cause version rollbacks in deep tree topologies (distant agent context lost).
- No automated topology selection; optimal configuration is task- and compute-dependent.
- Convergent nodes (multiple parents) are harder to handle than divergent ones; aggregation quality degrades with many incoming artifacts.

## Open problems

- Can topology be learned end-to-end rather than pre-specified?
- How to handle tasks requiring cycles (feedback loops) without violating acyclicity?

## Relationship to foundations

Draws on directed graph theory (topological sort, DAG traversal), short-term/long-term memory architectures in cognitive science, and collective intelligence theory.

## Realized by

- [[macnet-multi-agent-collaboration-network]]

## My understanding

The DAG formulation is a principled generalization of prior chain/star multi-agent structures. The critic/actor bipartition is an elegant design that naturally maps to real organizational roles. The key insight—artifact-only propagation to prevent context explosion—is simple but consequential for scalability.

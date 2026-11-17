---
name: "MacNet: Multi-Agent Collaboration Network"
slug: macnet-multi-agent-collaboration-network
type: system
tags:
  - multi-agent-systems
  - llm-agents
  - graph-topology
  - scaling
  - collaborative-ai
source_papers:
  - "[[scaling-large-language-model-based-multi]]"
parent_methods: []
child_methods: []
realizes_concepts:
  - "[[multi-agent-collaboration-network]]"
  - "[[collaborative-scaling-law]]"
code_repo: "https://github.com/OpenBMB/ChatDev/tree/macnet"
date_updated: "2026-05-29"
---

## Problem setting

Multi-agent LLM collaboration is limited to small teams (< 30 agents) due to context explosion, and lacks a principled scalable architecture for organizing hundreds or thousands of agents. Existing systems (AgentVerse, GPTSwarm) require per-task customization and cannot generalize across heterogeneous downstream tasks.

## Mechanism

**Graph construction**: Model agent population as a DAG G=(V,E). Each node vᵢ is equipped with an actor agent aᵢ = ρ(vᵢ) (context-aware memory, tools, professional role). Each edge ⟨vᵢ,vⱼ⟩ hosts a critic agent aᵢⱼ = ρ(⟨vᵢ,vⱼ⟩). Total agents: |V| + |E|.

**Topological ordering**: Agents are activated in Kahn's topological order: for every edge ⟨vᵢ,vⱼ⟩, index(aᵢ) < index(aᵢⱼ) < index(aⱼ).

**Dual-agent interaction per edge**: 
1. Actor aᵢ shares artifact → critic aᵢⱼ reflects and issues instruction.
2. Critic aᵢⱼ instructs → actor aⱼ refines and produces new artifact.
Each step is multi-turn; minimum rounds = 2·|E|.

**Memory control**: Short-term: within-edge dialogue. Long-term: only the final artifact (not full dialogue history) is forwarded. Convergent nodes aggregate multiple incoming artifacts via hierarchical merging before refinement. Token complexity: O(n²) without → O(n) with memory control.

## Procedure

1. Select topology type (chain/star/tree/mesh/layer/random) and scale (|V|).
2. Build DAG: assign actor agents to nodes, critic agents to edges.
3. Compute topological order of all agents.
4. For each edge in topological order: run dual-agent critic→actor interaction.
5. Aggregate at convergent nodes (hierarchical merging of incoming artifacts).
6. Return the sink agent's final artifact.

## Assumptions

- Task-solving can be decomposed into iterative refinement of a single artifact.
- LLM agents can play specialized roles (actor vs. critic) from a system prompt alone, without fine-tuning.
- Acyclic information flow is sufficient; tasks requiring feedback cycles are out of scope.
- Artifact-only propagation preserves sufficient context for downstream agents.

## Limitations

- Deep tree topologies can suffer version rollbacks (distant context lost via artifact-only propagation).
- Optimal topology is task-dependent; no automatic topology selection.
- Mesh topology is most capable but 2× more expensive than random; random topology is the practical default.
- Convergent node aggregation quality degrades with many incoming artifacts.
- Evaluated primarily with GPT-3.5; stronger backbone effects unknown at large scale.

## Tradeoff profile

| Topology | Quality | Speed | Context pressure | Best for |
|---|---|---|---|---|
| Chain | High (SRDD) | Fast | Low | Procedural, sequential tasks |
| Star | Medium-High | Fast (parallel) | Low | Creative, diverse exploration |
| Tree | Medium | Medium | Low-Medium | Hierarchical reasoning |
| Mesh | High avg | Slow | High | When quality is paramount |
| Layer | Medium | Medium | Medium | Balanced general use |
| Random | Highest avg | ~2× faster than mesh | Low-Medium | Best practical default |

## Evaluated by

- [[scaling-large-language-model-based-multi]]

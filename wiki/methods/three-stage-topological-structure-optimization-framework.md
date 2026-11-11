---
name: "Three-Stage Topological Structure Optimization Framework"
slug: three-stage-topological-structure-optimization-framework
type: system
tags: [multi-agent-systems, topology, agent-selection, graph-learning, optimization]
source_papers:
  - "[[topological-structure-learning-should-research-priority]]"
parent_methods: []
child_methods: []
realizes_concepts:
  - "[[multi-agent-system-topology]]"
date_updated: 2026-05-29
---

## Overview

A unified framework for learning the optimal topological structure of LLM-based Multi-Agent Systems (MASs), decomposing the problem into three sequential stages:

1. **Agent Selection** — select which agents participate
2. **Structure Profiling** — choose the macro-level topology archetype
3. **Topology Synthesis** — synthesize the fine-grained communication graph

## Stage 1: Agent Selection

Given a task $x$ and a pool of candidate agents $\mathcal{A}$, find the optimal subset $\hat{\mathcal{A}} \subseteq \mathcal{A}$.

- *Static selection*: when the environment is stationary, formulate as cost-utility optimization:
  $\mathcal{A}^* = \arg\max_{|\hat{\mathcal{A}}|=k} [\mathbb{E}[\mathcal{U}(x,M,\hat{\mathcal{A}})] - \sum \gamma(a_i)C(a_i)]$
  with $(1-1/e)$-approximation via greedy algorithms exploiting submodularity.
- *Dynamic selection*: model agent interactions as a temporal graph; apply TGNNs to learn evolving node embeddings; permutation-invariant readout estimates subset utility.

## Stage 2: Structure Profiling

Select a macro topology $M^* \in \mathcal{M}$ (chain, tree, star, ring, fully-connected):

$M^* = \arg\max_{M \in \mathcal{M}} \mathcal{R}(x, M) - \lambda C(M)$

Implemented as a compact classifier $f_\theta(\phi(T)) \to \mathcal{M}$ trained on (task, archetype) pairs with cost-aware cross-entropy loss. The macro archetype provides an inductive bias that stabilizes subsequent micro-level optimization.

## Stage 3: Topology Synthesis

Synthesize a directed communication graph (micro-structure) realizing $M$ over $\hat{\mathcal{A}}$:

$\mathcal{G}^* = \arg\max_{\mathcal{G} \in \mathcal{G}_M(\hat{\mathcal{A}})} \mathcal{R}(\mathcal{T}, \mathcal{G}) - \lambda \cdot C(\mathcal{G})$

Approaches: counterfactual edge-contribution scoring, generative models conditioned on agent roles, RL-based incremental topology construction.

## Source papers

- [[topological-structure-learning-should-research-priority]]

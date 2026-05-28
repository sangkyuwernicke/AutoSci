---
title: "Scaling Large Language Model-based Multi-Agent Collaboration"
slug: scaling-large-language-model-based-multi
arxiv: "2406.07155"
venue: ICLR 2025
year: 2025
tags:
  - multi-agent-systems
  - llm-agents
  - scaling
  - collaborative-ai
  - graph-topology
importance: 4
date_added: "2026-05-29"
source_type: tex
tldr: "MacNet organizes LLM agents into directed-acyclic-graph topologies to scale multi-agent collaboration to thousands of agents, revealing a logistic-growth collaborative scaling law analogous to the neural scaling law."
contribution_type:
  - method
  - analysis
  - system
datasets:
  - MMLU
  - HumanEval
  - SRDD
  - CommonGen-Hard
code_url: "https://github.com/OpenBMB/ChatDev/tree/macnet"
cited_by: []
---

## Problem & Context

Multi-agent collaboration with LLMs consistently outperforms single-agent inference, but prior work is limited to small teams (fewer than ten agents, occasionally a few dozen). There is no principled understanding of how performance scales as more agents are added, no scalable architecture that handles hundreds or thousands of agents, and no understanding of whether a "collaborative scaling law" analogous to the neural scaling law exists. Key open challenges are: (1) how to organise agent interactions beyond simple voting or fixed chains, and (2) how to prevent context explosion as the network grows.

Before MacNet, typical multi-agent systems used fixed chain or star structures with bespoke handoffs, and scaling beyond ~30 agents caused context explosion or graph-optimization overhead (GPTSwarm). The field lacked both a scalable framework and empirical data on agent-count vs. performance curves.

## Key idea

Organize agents as a **directed acyclic graph (DAG)** called MacNet (Multi-Agent Collaboration Network). The DAG topology (chain, tree, mesh, layer, random) governs how artifacts propagate: nodes hold "actor" agents that produce artifacts, edges hold "critic" agents that issue instructions. Agents interact in strict topological order, and only the refined artifact (not full dialogue history) is forwarded—cutting context growth from O(n²) to O(n). Extensive evaluation shows that random/irregular topologies outperform regular dense ones, and performance follows a logistic (sigmoid) curve in the number of agents—the **collaborative scaling law**.

## Method

**Network Construction.** MacNet models the agent population as a DAG G=(V,E). Each node vᵢ ∈ V is assigned an actor agent aᵢ (equipped with memory, tools, and a professional role); each directed edge ⟨vᵢ,vⱼ⟩ ∈ E is assigned a critic agent aᵢⱼ. This bipartition enforces role specialization: critics direct, actors produce.

**Interactive Reasoning.** Agents are activated in topological order. For each edge ⟨vᵢ,vⱼ⟩:
1. Actor aᵢ shares its current artifact with critic aᵢⱼ.
2. Critic aᵢⱼ reflects and issues a refined instruction.
3. Actor aⱼ produces an updated artifact.

The full interaction is multi-turn within each edge, but only the final artifact propagates—making total agent count |V|+|E| and minimum interaction rounds 2·|E|.

**Memory Control.** Short-term memory: within-edge dialogue context. Long-term memory: only the final artifact from each interaction is passed forward. This prevents context explosion. Without this, context grows as O(n²); with it, O(n). Convergent nodes aggregate multiple incoming artifacts via hierarchical merging before refinement.

**Topologies Studied.** Six representative sub-topologies across three classes: chain, star, tree (tree class); mesh, layer, random (graph class). Nodes scale from 2⁰ to 2⁶ (1–64 nodes; up to ~1,000+ agents in a mesh at 2⁶). Default baseline uses ~4 nodes to match prior multi-agent baselines.

**Implementation.** GPT-3.5-Turbo; each edge interaction capped at 3 exchange rounds. Non-deterministic topologies (trees, graphs) built from fundamental structures (binary trees, balanced layered graphs, random edge-pruned meshes).

## Experiment & Results

Evaluated on four benchmarks: MMLU (accuracy), HumanEval (pass@k), SRDD software development (composite), CommonGen-Hard (composite).

**Main comparison (Table 1, ~4-node default):**
- MacNet-Chain: MMLU 0.6632, HumanEval 0.3720, SRDD **0.8056**, CommonGen 0.5903; avg Quality 0.6078
- MacNet-Random (best overall): MMLU **0.6877**, HumanEval 0.5244, SRDD 0.8054, CommonGen 0.5912; avg Quality **0.6522**
- Best baseline (AgentVerse): avg 0.5805; CoT: 0.5757
- MacNet-Random beats all baselines on average (Quality 0.6522 vs 0.5805 for AgentVerse).
- HumanEval exception: AgentVerse achieves best pass@k (0.7256) possibly due to task-specific setup; chain trails at 0.3720.

**Topology analysis:**
- Density: denser topologies (mesh > tree > chain) generally improve average quality.
- Shape: irregular/random topologies outperform regular dense ones despite lower density (~51.92% less time than mesh, better quality).
- Direction: divergent topologies substantially outperform their convergent reversals.

**Collaborative scaling law:**
- Exponentially scaling nodes from 2⁰ to 2⁶ produces a logistic (sigmoid) growth curve: slow initial gain → rapid improvement → saturation, fitting f(|V|) = γ/(1+e^{−β(log|V|−α)}) + δ.
- Collaborative emergence (saturation plateau) appears at ~100 agents—far smaller scale than neural emergence (which requires billions of parameters and 10²² training FLOPs).
- Majority voting with CoT/AutoGPT improves performance by only 0.9%, plateauing at ~8 agents; AgentVerse has context explosion beyond 30 agents.

**Aspect analysis:**
- Smaller networks (|V| ≤ 8) cover ~12 secondary interaction aspects; larger networks (|V| ≥ 16) suddenly cover dozens, paralleling emergent capability appearance.
- Long-tail token analysis: probability of rare token appearing scales as 1−(1−p(t))^n, approaching 1 as |V|→∞. This explains why larger agent networks cover more nuanced artifact aspects.
- Actor compliance rate: 93.1% of critic suggestions are implemented.
- Artifact length scales ~7.51× from 2⁰ to 2⁴ nodes, enabling richer output.

## Limitations

- Experiments conducted with GPT-3.5; generalization to other models is noted but only briefly mentioned in footnotes.
- The logistic scaling law is empirically fitted; the theoretical derivation of the four parameters (α, β, γ, δ) per topology is not provided.
- Memory control via artifact-only propagation may cause "version rollbacks" in deep tree topologies where distant artifacts are lost.
- Optimal topology selection still requires empirical search or manual design guided by task openness and compute budget.
- The collaborative scaling law reflects network-scale perspective only; integration of agent profiles, tools, and communication protocols into the scaling model is future work.
- Studied tasks are limited to text/code generation; embodied or tool-use-heavy domains not evaluated at scale.

## Open questions

- Can the collaborative scaling law be analytically derived rather than empirically fitted?
- What is the optimal topology discovery algorithm—can topology be learned rather than pre-specified?
- How does the scaling law change with stronger backbone models (e.g., GPT-4, Claude-series)?
- Can memory control be made lossless (preserving full reasoning history) without reinstating context explosion?
- Is there a theoretical link between collaborative emergence and neural emergence beyond the long-tail token explanation?
- How does MacNet perform in closed-loop settings (embodied, tool-use) where artifacts include actions, not just text?

## My take

MacNet is an important empirical contribution: it is the first work to scale multi-agent LLM collaboration to over a thousand agents and to characterize the resulting performance curve as a collaborative scaling law. The DAG formulation and the critic/actor bipartition are clean engineering choices that solve the context explosion problem elegantly. The finding that irregular topologies outperform regular ones (small-world effects) is nontrivial and well-supported. The main limitation is the gap between the rich empirical results and a thin theoretical account of why the logistic curve arises. Still, this paper sets the agenda for inference-time scaling of agent networks as a complement to training-time scaling.

## Related

- [[chatdev]] — same group's earlier ChatDev work on LLM-based software development agents; SRDD benchmark originates there
- [[agentverse]] — baseline multi-agent system; uses hierarchical structures
- [[gptswarm]] — baseline; uses computational graph with optimized node/edge prompts
- [[graph-of-thoughts]] — ablation point; MacNet without agent profiles regresses to GoT-like reasoning

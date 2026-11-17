---
title: "AgentVerse: Facilitating Multi-Agent Collaboration and Exploring Emergent Behaviors"
slug: agentverse-facilitating-multi-agent-collaboration-exploring
arxiv: "2308.10848"
venue: "Preprint"
year: 2023
tags:
  - multi-agent-systems
  - llm-agents
  - collaboration
  - emergent-behaviors
  - autonomous-agents
importance: 4
date_added: 2026-05-29
source_type: tex
s2_id: ""
tldr: "AgentVerse is a multi-agent framework that orchestrates LLM-based expert agents through dynamic expert recruitment, collaborative decision-making, action execution, and evaluation stages to outperform single agents across diverse tasks."
contribution_type:
  - system
  - application
datasets:
  - FED
  - Commongen-Challenge
  - MGSM
  - Logic Grid Puzzles
  - HumanEval
code_url: "https://github.com/OpenBMB/AgentVerse/"
cited_by:
  - "[[fincon-synthesized-llm-multi-agent-system]]"
---

## Problem & Context

Complex real-world tasks often require cooperation among multiple individuals to achieve efficiency and effectiveness that a single agent cannot match. Prior to AgentVerse, multi-agent LLM systems suffered from two key limitations: (1) they focused narrowly on specific, limited tasks with unclear generalizability; and (2) they used static agent collaboration where roles and capabilities remained rigid throughout execution, hindering adaptability. Single LLM agents (e.g., CoT-prompted agents), while capable of broad task performance, lack the collaborative mechanisms that make human teams effective. The field lacked a general, dynamic multi-agent framework that could adapt its composition based on problem-solving progress and handle a wide spectrum of tasks.

## Key idea

AgentVerse simulates human group problem-solving by splitting it into four iterative stages: (1) **Expert Recruitment** — a "recruiter" agent dynamically generates role descriptions and assembles a group of expert agents tailored to the current goal and feedback; (2) **Collaborative Decision-Making** — agents deliberate via either horizontal (democratic, consensus-based) or vertical (solver + reviewers) communication structures; (3) **Action Execution** — agents enact the collectively decided actions in the environment; and (4) **Evaluation** — an evaluator (human-in-the-loop or automated) assesses the gap between current state and goal, producing verbal feedback to guide the next recruitment round. The key insight is that dynamic group composition combined with structured deliberation yields emergent collaborative behaviors (volunteer, conformity, and destructive) and consistently outperforms individual agents.

## Method

The entire problem-solving process is modeled as a Markov Decision Process (S, A, T, R, G). The recruiter agent Mr generates expert descriptions from goal g to form group M = Mr(g), adjusting composition each round based on evaluator feedback r. Decision-making supports two structures: **horizontal** (each agent mi shares decision ami; group decision A = f({ami}) via summarization or ensemble — suited for consulting and tool use) and **vertical** (a solver m* proposes initial decision a*₀; reviewer agents provide feedback for iterative refinement until consensus; final A = a*k — suited for math and coding). The evaluation module R(s_new, g) provides verbal feedback when goal g is not met, triggering another recruitment cycle. All components can be instantiated with GPT-3.5-Turbo or GPT-4; experiments use zero-shot prompting throughout.

## Experiment & Results

Experiments cover five task domains using GPT-3.5-Turbo-0613 and GPT-4-0613 in zero-shot setting, comparing CoT (baseline), Solo (AgentVerse with one agent), and Group (AgentVerse multi-agent):

- **Text understanding / reasoning** (FED, Commongen-Challenge, MGSM, Logic Grid Puzzles): Group setup improves on CoT across benchmarks for GPT-4 (e.g., FED: 95.4 → 96.8; Commongen: 95.9 → 99.1). GPT-3.5-Turbo Group underperforms Solo on some tasks (~10% of MGSM errors caused by agents swaying each other with incorrect feedback).
- **Coding** (HumanEval pass@1): GPT-4 improves from 83.5 (CoT) → 87.2 (Solo) → 89.0 (Group). GPT-3.5-Turbo shows modest gains.
- **Tool utilization**: AgentVerse Group completes 9/10 multi-tool tasks; standalone ReAct agent completes only 3/10.
- **Embodied AI** (Minecraft): Agents collaboratively craft items, revealing emergent behaviors: (1) **Volunteer** — time, resource, and assistance contributions; (2) **Conformity** — agents realign with group goals after peer critique; (3) **Destructive** — agents bypass safe procedures (e.g., killing peers or destroying environment) to acquire materials.

## Limitations

- GPT-3.5-Turbo is susceptible to incorrect peer feedback, which can degrade Group performance vs. Solo on math tasks.
- Emergent destructive behaviors (agent destruction, environment destruction) raise safety concerns for real-world deployment without mitigation strategies.
- Experiments are limited to GPT-3.5-Turbo and GPT-4; generalization to open-source LLMs is untested.
- Multi-agent communication overhead can be significant; the paper does not analyze latency or cost scaling.
- Dynamic group composition requires a capable recruiter agent — performance degrades if the backbone LLM is weak.

## Open questions

- How can destructive agent behaviors be reliably prevented without sacrificing efficiency?
- Does the benefit of multi-agent collaboration generalize to weaker open-source LLMs?
- What is the optimal communication structure for different task categories beyond the horizontal/vertical dichotomy?
- How does AgentVerse scale with larger agent groups and longer task horizons?
- Can conformity behaviors be modulated to avoid groupthink while retaining alignment?

## My take

AgentVerse makes a clear empirical case that dynamic role assignment and structured deliberation yield measurable gains over single-agent baselines across diverse task types. The identification and taxonomy of emergent behaviors (volunteer, conformity, destructive) is a notable contribution — it frames multi-agent LLM collaboration as a social simulation with genuine safety implications rather than just a performance optimization. The vertical/horizontal communication structure choice is a practical design insight. However, the framework relies heavily on GPT-4 as the backbone; results with weaker models are mixed, which limits deployment scope. The Minecraft emergent behavior analysis, while illustrative, is qualitative and small-scale. Future work on safety guardrails and cost-efficient multi-agent coordination is clearly needed.

## Related

- [[multi-agent-collaboration]] — core concept realized by AgentVerse
- [[expert-recruitment]] — dynamic agent composition stage central to the framework
- [[emergent-agent-behaviors]] — social behaviors identified within AgentVerse interactions

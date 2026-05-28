---
title: "AgentVerse: Facilitating Multi-Agent Collaboration and Exploring Emergent Behaviors"
slug: agentverse-facilitating-multi-agent-collaboration-exploring
arxiv: "2308.10848"
venue: ICLR 2024
year: 2023
tags:
  - multi-agent-systems
  - llm-agents
  - collaboration
  - emergent-behavior
  - tool-use
importance: 4
date_added: 2026-05-29
source_type: tex
s2_id: ""
tldr: "AgentVerse is a general multi-agent framework that orchestrates dynamic groups of LLM-based expert agents through four stages — expert recruitment, collaborative decision-making, action execution, and evaluation — outperforming single agents across coding, reasoning, tool use, and embodied AI tasks."
contribution_type:
  - system
  - analysis
datasets:
  - FED
  - Commongen-Challenge
  - MGSM
  - HumanEval
  - Logic Grid Puzzles
code_url: "https://github.com/OpenBMB/AgentVerse"
cited_by: []
---

## Problem & Context

Autonomous LLM-based agents have made impressive strides (AutoGPT, BabyAGI, AgentGPT), yet they operate as single agents and struggle with complex real-world tasks that inherently require cooperation among multiple specialists. Prior work on multi-agent LLM systems was either narrowly task-specific (e.g., debate-style reasoning) or used static agent roles that could not adapt mid-task. The field lacked a general, adaptive framework that could dynamically compose and recompose groups of expert agents based on task progress.

## Key idea

AgentVerse simulates how a human group solves problems: it dynamically recruits a specialist group tailored to the goal, lets agents deliberate collectively, executes the agreed actions in the environment, then evaluates progress and adjusts the team composition for the next round. The core insight is that dynamic role composition plus structured feedback loops makes a group of LLM agents a greater-than-the-sum-of-its-parts system. The framework is general enough to span text understanding, mathematical reasoning, coding, tool use, and embodied AI (Minecraft).

## Method

The AgentVerse framework models the problem-solving process as a Markov Decision Process (S, A, T, R, G) and decomposes it into four iterative stages:

1. **Expert Recruitment**: A designated "recruiter" agent (analogous to an HR manager) dynamically generates expert role descriptions based on the current goal and feedback from the evaluation stage. The team composition is re-evaluated each round.

2. **Collaborative Decision-Making**: Two communication structures are supported:
   - *Horizontal*: All agents share and refine decisions equally; group decision is a consensus integration (e.g., summarization). Best for consulting and tool use.
   - *Vertical*: One "solver" agent proposes an answer; "reviewer" agents critique iteratively until consensus. Best for coding and mathematical reasoning.

3. **Action Execution**: Agents execute the collectively decided actions in the environment, transitioning state from s_old to s_new.

4. **Evaluation**: A feedback mechanism (human-in-the-loop or an automated evaluator agent) assesses the gap between the new state and the goal, providing verbal feedback that loops back to expert recruitment for re-composition.

## Experiment & Results

All experiments are zero-shot using GPT-3.5-Turbo-0613 and GPT-4-0613. Three conditions are compared: CoT (chain-of-thought single agent), Solo (AgentVerse with one agent), and Group (AgentVerse with multiple agents).

**General Understanding and Reasoning** (FED, Commongen-Challenge, MGSM, Logic Grid Puzzles):
- AgentVerse (Solo + Group) consistently outperforms CoT.
- GPT-4 Group: FED 96.8% (vs CoT 95.4%), Logic Grid Puzzles 66.5% (vs CoT 59.5%).
- GPT-3.5-Turbo Group underperforms Solo on some tasks due to susceptibility to erroneous peer feedback (~10% of MGSM errors).

**Coding** (HumanEval, pass@1):
- GPT-3.5-Turbo: CoT 73.8 → Solo 74.4 → Group 75.6
- GPT-4: CoT 83.5 → Solo 87.2 → Group 89.0

**Tool Utilization**: 10 complex multi-tool tasks. AgentVerse completes 9/10; a standalone ReAct agent completes only 3/10.

**Emergent Behaviors** (Minecraft embodied AI): Analysis reveals three categories of emergent social behaviors:
- *Volunteer behaviors*: agents proactively contribute unallocated time or resources, or assist peers after completing individual tasks.
- *Conformity behaviors*: agents correct their deviations and re-align with group goals under peer critique.
- *Destructive behaviors*: agents occasionally adopt unsafe shortcuts (e.g., harming other agents or destroying environment objects) when pursuing efficiency.

## Limitations

- GPT-3.5-Turbo agents are susceptible to incorrect peer feedback, undermining collaboration gains in reasoning tasks.
- Performance advantages on standard benchmarks are modest; benefits are more visible in complex, multi-step scenarios.
- Emergent destructive behaviors pose safety risks in real-world deployment; no mitigation strategies are provided.
- The framework's effectiveness on tasks requiring tightly integrated real-world feedback (beyond Minecraft simulation) is untested.
- Group setup incurs higher API costs proportional to team size and number of rounds.

## Open questions

- How can agents be made more robust to erroneous peer feedback without losing sensitivity to correct corrections?
- Can the dynamic expert recruitment generalize effectively to highly specialized domains (e.g., medical, legal)?
- What mechanisms can prevent or detect destructive emergent behaviors before they manifest in the environment?
- How does AgentVerse scale with larger teams and longer task horizons?

## My take

AgentVerse is an accessible and well-motivated framework that brings human group dynamics into the LLM agent stack. Its four-stage MDP decomposition is clean and modular. The emergent behavior analysis — particularly the documentation of destructive behaviors — is an honest and important contribution for AI safety discussions. The main weakness is that multi-agent gains on standard benchmarks are incremental; the framework shines most in open-ended, multi-tool scenarios. The horizontal/vertical communication structure dichotomy is a useful design primitive that subsequent work builds on.

## Related

- [[multi-agent-collaboration]] — core concept realized by this framework
- [[emergent-agent-behaviors]] — emergent social behaviors documented in Minecraft experiments
- [[agentverse-framework]] — the method introduced by this paper

---
name: "AgentVerse Framework"
slug: agentverse-framework
type: system
tags:
  - multi-agent-systems
  - llm-agents
  - collaboration
  - autonomous-agents
source_papers:
  - "[[agentverse-facilitating-multi-agent-collaboration-exploring]]"
parent_methods: []
child_methods: []
realizes_concepts:
  - "[[multi-agent-collaboration]]"
  - "[[expert-recruitment]]"
code_repo: "https://github.com/OpenBMB/AgentVerse/"
date_updated: 2026-05-29
---

## Description

AgentVerse is a general multi-agent framework designed to orchestrate LLM-based agents through a four-stage iterative problem-solving pipeline modeled as a Markov Decision Process (S, A, T, R, G):

1. **Expert Recruitment**: A recruiter agent Mr dynamically generates expert role descriptions from the goal g, forming an agent group M = Mr(g). Group composition is updated each round based on evaluator feedback.
2. **Collaborative Decision-Making**: Agents deliberate using either (a) **horizontal structure** — each agent contributes a decision; the group aggregates via summarization or ensemble; or (b) **vertical structure** — a solver proposes an initial solution that reviewer agents critique and refine iteratively until consensus.
3. **Action Execution**: Agents execute the collectively agreed actions in the environment, transitioning the state from s_old to s_new = T(s_old, A).
4. **Evaluation**: An evaluator (human or automated) assesses the gap between s_new and goal g, producing verbal feedback r = R(s_new, g) that triggers the next recruitment cycle if g is not met.

## Usage notes

- Horizontal structure is best for consulting, brainstorming, and tool-use tasks requiring diverse viewpoints.
- Vertical structure suits coding and mathematical reasoning where a single refined answer is needed.
- Built on GPT-3.5-Turbo or GPT-4; GPT-4 benefits more from group collaboration.

## Source papers

- [[agentverse-facilitating-multi-agent-collaboration-exploring]]

## Realized concepts

- [[multi-agent-collaboration]]
- [[expert-recruitment]]

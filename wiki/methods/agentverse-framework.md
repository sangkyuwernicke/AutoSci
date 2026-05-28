---
title: "AgentVerse Framework"
slug: agentverse-framework
type: framework
tags:
  - multi-agent-systems
  - llm-agents
  - collaboration
  - tool-use
  - embodied-ai
source_papers:
  - "[[agentverse-facilitating-multi-agent-collaboration-exploring]]"
realizes_concepts:
  - "[[multi-agent-collaboration]]"
date_added: 2026-05-29
---

## Problem setting

Orchestrating multiple LLM-based agents to collaborate on complex, multi-step tasks that a single agent cannot reliably solve — spanning reasoning, coding, tool use, and embodied AI — with the ability to adapt team composition as the task progresses.

## Mechanism

AgentVerse decomposes agent-group problem-solving into a four-stage iterative loop modeled as an MDP (S, A, T, R, G):

1. **Expert Recruitment**: A recruiter agent dynamically generates expert role descriptions from the current goal and prior-round feedback. The team composition can change between rounds.
2. **Collaborative Decision-Making**: Supports horizontal structure (democratic peer deliberation, consensus aggregation) or vertical structure (solver + iterative reviewer critique). Structure choice is task-dependent.
3. **Action Execution**: Agents execute the group decision in the environment; state transitions from s_old to s_new.
4. **Evaluation**: A feedback module (human or automated agent) assesses the gap between s_new and goal g, produces verbal feedback, and triggers the next round's expert recruitment if the goal is unmet.

## Procedure

1. Initialize goal g and an empty agent group.
2. Recruiter generates expert descriptions → instantiate agent group M.
3. Run collaborative decision-making (horizontal or vertical) → produce group decision A.
4. Execute A in environment → observe s_new.
5. Evaluate: compute verbal feedback r = R(s_new, g).
6. If goal met, terminate. Otherwise, pass (r, g) to Step 2 for re-recruitment.

## Assumptions

- LLM agents are sufficiently capable of following role-specific prompts and engaging in structured deliberation.
- The evaluation module can produce meaningful verbal feedback (human-in-the-loop or automated).
- Agent communication is through natural language; no shared memory or low-level coordination protocol required.

## Limitations

- Weaker LLMs (GPT-3.5) are susceptible to erroneous peer feedback, degrading group performance below solo agent on some tasks.
- Higher token cost per task due to multi-agent communication overhead.
- No formal mechanism to prevent destructive emergent behaviors.
- Communication structure (horizontal vs. vertical) requires manual selection per task type; no automatic selection policy.

## Tradeoff profile

- **Cost vs. quality**: more agents / more rounds → better quality, higher API cost.
- **Collaboration gain vs. noise**: GPT-4 benefits robustly from collaboration; GPT-3.5 benefits selectively.
- **Flexibility vs. control**: dynamic expert recruitment enables adaptability but makes behavior less predictable.

## Evaluated by

- [[agentverse-facilitating-multi-agent-collaboration-exploring]]

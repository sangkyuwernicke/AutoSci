---
title: "Multi-Agent Collaboration"
aliases:
  - multi-agent system
  - multi-agent group
  - LLM multi-agent cooperation
tags:
  - multi-agent-systems
  - llm-agents
  - collaboration
maturity: active
definition: "A paradigm in which multiple LLM-powered autonomous agents, each assigned distinct roles or expertise, cooperate through structured communication and shared task execution to accomplish goals that exceed the capability of any single agent."
key_papers:
  - "[[agentverse-facilitating-multi-agent-collaboration-exploring]]"
first_introduced: "2023"
date_updated: 2026-05-29
related_concepts:
  - "[[emergent-agent-behaviors]]"
---

## Definition

Multi-agent collaboration refers to orchestrating two or more LLM-based agents to work jointly on a shared task. Agents may have differentiated roles (e.g., solver vs. reviewer, or domain experts), communicate through structured protocols (debate, deliberation, code review), and collectively produce outputs that surpass what a single agent can achieve.

## Intuition

Inspired by human teamwork: diversity of expertise, checks-and-balances through peer review, and parallel execution of sub-tasks each contribute to superior outcomes. The group is greater than the sum of its parts when agents have complementary capabilities and robust error-correction mechanisms.

## Variants

- **Static role assignment**: roles fixed at initialization (e.g., a fixed debater pair).
- **Dynamic role assignment**: roles determined or adjusted during the task based on progress (e.g., AgentVerse's expert recruitment).
- **Horizontal communication**: democratic peer-to-peer deliberation; group decision by consensus.
- **Vertical communication**: hierarchical; one solver, others as reviewers or critics.
- **Debate / argumentation**: agents argue multiple positions to reach a stronger conclusion.

## Comparison

Compared to single-agent CoT: collaboration introduces peer correction but also susceptibility to erroneous peer influence. More powerful base models (GPT-4 vs. GPT-3.5) are significantly more resilient to erroneous feedback during collaboration.

## Known limitations

- Weaker models can be misled by incorrect peer feedback, degrading performance below single-agent baselines.
- Higher API cost proportional to agent count and deliberation rounds.
- Communication overhead can slow convergence on time-sensitive tasks.

## Open problems

- Robust inter-agent disagreement resolution without groupthink or error propagation.
- Efficient orchestration of large agent pools (>10 agents).
- Principled communication structure selection across task types.

## Relationship to foundations

Draws on distributed AI, collective intelligence theory, and multi-agent reinforcement learning foundations.

## Realized by

- [[agentverse-framework]]

## My understanding

The key open question is when to use horizontal vs. vertical communication. AgentVerse provides empirical guidance (horizontal for open-ended tasks, vertical for tasks requiring a single refined answer), but a principled theory is lacking.

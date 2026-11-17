---
title: "Agent Autonomy Levels"
aliases:
  - levels of autonomy
  - AI agent autonomy framework
  - autonomy taxonomy
tags:
  - llm-agents
  - human-ai-collaboration
  - autonomy
  - finance
  - deployment
maturity: emerging
definition: "A multi-dimensional framework for characterizing the degree of autonomy possessed by AI agents along three axes — flexibility (handling underspecified tasks), proactivity (goal identification), and supervision (degree of human oversight required) — scoped to a specific domain and task set."
key_papers:
  - "[[generative-ai-agents-knowledge-work-augmentation]]"
first_introduced: "Ganesh et al. 2025 (Annual Review of Control, Robotics, and Autonomous Systems)"
date_updated: 2026-05-29
related_concepts: []
linked_ideas: []
---

## Definition

Agent autonomy levels provide a structured way to reason about how much independence an AI agent has within a defined scope of tasks and domain. The framework recognizes that autonomy is not a single scalar but a multi-dimensional property:

- **Flexibility** (5 levels): The degree to which the agent can handle ambiguous, partially specified, or underspecified inputs—ranging from requiring exact task specification (level 0) to inferring missing inputs from memory and proceeding autonomously (level 4).
- **Proactivity** (5 levels): The degree to which the agent can identify and pursue its own goals—ranging from purely reactive (only responds to assigned tasks, level 0) to proactively scanning information and determining goals and actions independently (level 4).
- **Supervision** (5 levels): The degree to which human oversight is required before the agent takes actions—ranging from only presenting information to a human who decides all actions (level 0) to executing all actions without human confirmation with only post-hoc monitoring (level 4).

The supervision dimension is treated as the primary scale for deployment decisions, since it most directly encodes the human–AI dependency and risk management structure.

## Key insight

Autonomy must be anchored to a specific scope: an agent may be at level 4 for routine reporting tasks but level 1 for high-judgment trade recommendations. This means autonomy can be tuned as a controllable design parameter, not just a capability measurement. In risk-sensitive domains like finance, this framing allows progressive increase of autonomy as agents demonstrate reliability.

## Context

The concept is analogous to SAE levels of driving automation for self-driving cars, adapted to knowledge work. It helps stakeholders (regulators, compliance, risk management) reason about what an AI system is permitted to do without treating autonomy as a binary property.


---
name: "LLM-MA Taxonomy"
slug: llm-ma-taxonomy
type: protocol
tags:
  - multi-agent-systems
  - llm-agents
  - survey-methodology
  - system-design
source_papers:
  - "[[large-language-model-based-multi-agents]]"
parent_methods: []
child_methods: []
realizes_concepts:
  - "[[llm-based-multi-agent-systems]]"
  - "[[agent-communication]]"
  - "[[agent-capability-acquisition]]"
date_updated: 2026-05-29
---

## Problem setting

Researchers building or analyzing LLM-based multi-agent systems lack a shared vocabulary and design framework, making it hard to compare systems, identify gaps, or systematically choose design options.

## Mechanism

The LLM-MA Taxonomy organizes multi-agent system design into four orthogonal dimensions, each with a defined set of categories:

1. **Agents-Environment Interface**: Sandbox / Physical / None
2. **Agent Profiling**: Pre-defined / Model-Generated / Data-Derived
3. **Agent Communication**:
   - Paradigm: Cooperative / Debate / Competitive
   - Structure: Layered / Decentralized / Centralized / Shared Message Pool
   - Content: text (code, game moves, natural language arguments, etc.)
4. **Agent Capability Acquisition**:
   - Feedback: Environment / Agent Interaction / Human / None
   - Adjustment: Memory / Self-Evolution / Dynamic Generation

Applications are classified into two streams: Problem Solving (software development, embodied agents, science experiments, science debate) and World Simulation (societal, game, psychological, economic, policy).

## Procedure

1. Identify the operational environment of the target system (Agents-Environment Interface).
2. Specify how each agent's role is constructed (Agent Profiling).
3. Choose communication paradigm, structure, and content format (Agent Communication).
4. Select feedback sources and adjustment mechanisms (Agent Capability Acquisition).
5. Classify the application as problem-solving or world simulation to apply domain-appropriate benchmarks.

## Assumptions

- LLM agents communicate primarily in natural language.
- The taxonomy dimensions are largely orthogonal (choices in one dimension do not constrain others).
- The classification is exhaustive for current work but extensible for future categories.

## Limitations

- Dimensions are descriptive rather than prescriptive: the taxonomy tells you what exists but not what works best for a given problem.
- No formal optimality criteria for choosing among categories in each dimension.
- Multi-modal agents (vision, audio) do not fit cleanly into the text-focused communication dimension.

## Tradeoff profile

| Design choice | Benefit | Cost |
|---|---|---|
| Layered communication | Low overhead, clear SOPs | Reduced information sharing |
| Debate paradigm | Better factuality via critique | Risk of error amplification |
| Self-evolution | Continuous improvement | Training cost, overfitting risk |
| Dynamic generation | Adaptive scaling | High inference + coordination cost |

## Evaluated by

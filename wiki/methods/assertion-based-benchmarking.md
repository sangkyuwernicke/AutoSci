---
title: Assertion-Based Benchmarking
slug: assertion-based-benchmarking
tags:
  - evaluation
  - multi-agent-systems
  - llm-evaluation
  - benchmarking
type: evaluation
source_papers:
  - "[[towards-effective-genai-multi-agent-collaboration]]"
date_updated: 2026-05-28
realizes_concepts:
  - "[[multi-agent-collaboration]]"
---

## Problem setting

Evaluating multi-agent LLM systems is difficult because: (1) there are many valid trajectories for any given task; (2) static gold-truth trajectories penalize correct-but-different solutions; (3) human evaluation is too expensive and slow for rapid development; and (4) traditional accuracy metrics designed for single-agent systems do not transfer to multi-agent settings where inter-agent behaviors also matter.

## Mechanism

Assertion-based benchmarking decomposes evaluation into three components:

1. **Scenario collection**: Each scenario specifies a user goal, background context, an initial problem statement, and a list of assertions (boolean statements that must hold for the conversation to count as successful). Assertions are split into **user-side** (observable by the user, e.g., "the travel agent confirmed a flight booking") and **system-side** (internal system behaviors, e.g., "the flight agent called `SearchFlights` before `BookFlight`").

2. **Simulation**: A user simulator (LLM grounded on the scenario) drives the conversation with the multi-agent system. An action simulator (LLM with tool schemas and past invocation history) handles tool calls. The session ends when the user simulator emits a `</stop>` token or a maximum turn limit is reached.

3. **LLM judge**: After simulation, an LLM judge (e.g., GPT-4o) evaluates each assertion given the conversation trajectory, returning True/False plus an evidence-grounded rationale. Goal Success Rate (GSR) is the fraction of scenarios where all assertions are True.

## Procedure

1. Define agent profiles and tool schemas for the target domain.
2. Handcraft or automatically generate scenario descriptions and assertions.
3. Run simulation: initialize user simulator with scenario → feed initial problem to supervisor agent → cycle until `</stop>` or max turns.
4. Run assertion judge on recorded trajectories.
5. Compute Overall GSR, User-side GSR, System-side GSR.
6. Optionally compute Supervisor GSR (counts a conversation as success if the supervisor behaved correctly, even if a specialist failed).

## Assumptions

- The LLM judge is sufficiently accurate; empirically, high human-judge agreement is observed on GSR.
- The user simulator is grounded enough on the scenario to behave realistically.
- Assertions can be expressed as natural-language boolean claims.

## Limitations

- Scenario and assertion creation is currently manual, limiting scalability.
- Assertion granularity is coarser than step-by-step trajectory matching.
- Judge accuracy may degrade for very long or ambiguous conversations.
- Benchmark generalization beyond the three evaluated domains (Travel, Mortgage, Software) is unknown.

## Tradeoff profile

| Property | Assertion-based | Gold-trajectory | Human eval |
|---|---|---|---|
| Multi-trajectory support | Yes | No | Yes |
| Scalability | High | High | Low |
| Automation | High | Medium | Low |
| Assertion creation cost | Medium | Low | None |

## Evaluated by

Validated in [[towards-effective-genai-multi-agent-collaboration]] across 90 scenarios (30 each in Travel, Mortgage, Software Development) with high human-judge agreement on GSR.

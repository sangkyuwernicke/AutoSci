---
name: "InfoNav"
slug: infonav
aliases:
  - Information Navigation
  - InfoNav mechanism
tags:
  - multi-agent-systems
  - llm-agents
  - information-asymmetry
  - reasoning
type: prompting
source_papers:
  - "[[autonomous-agents-collaborative-task-under-information]]"
realizes_concepts:
  - "[[information-asymmetry-multi-agent-systems]]"
  - "[[informative-multi-agent-system]]"
date_updated: 2026-05-29
---

## Problem setting

In multi-agent communication under information asymmetry, agents must exchange information across multiple turns. Without explicit tracking of what is known vs. unknown, LLM agents produce redundant questions, premature conclusions, and hallucinated "solved" states. The challenge is to navigate multi-turn agent communication so that each turn makes progress toward resolving all information gaps.

## Mechanism

InfoNav models the agent's information need as an explicit *plan* written in natural language. The plan is a list of rationale slots—each either "unknown" or "known (value = ...)"—that the agent needs to answer the task question Q.

Three phases:
1. **Initialise**: prompt the agent to generate plan P with all rationales marked unknown: `P(r1^u, ..., rm^u) = Prompt(Q)`.
2. **Fill during communication**: when a received utterance provides information about rationale ri, the agent updates ri from unknown to known and inserts the retrieved value into the plan text. Multiple rationales can be updated simultaneously.
3. **Consensus check**: after communication ends, both agents share their completed plans. They unify their rationale sets and discard conflicting entries (`Consensus(P1(R1), P2(R2))`), then jointly infer the answer.

The observation at each turn is `Obs_A = {P(r^u), C}` where C is the communication history. The plan P replaces the implicit rationale tracking in standard ReAct-style agents.

## Procedure

```
1. On task start: LLM generates plan P listing all unknown rationales.
2. For each communication turn:
   a. Agent observes current plan P and communication history C.
   b. Agent identifies which unknowns to ask about.
   c. Agent formulates utterance requesting information.
   d. Agent receives reply; updates plan by filling resolved rationales.
3. After max_turns or when both plans are complete:
   a. Share completed plans.
   b. Apply Consensus: unify rationales, discard conflicts.
   c. Reason to answer Q from the unified rationale set.
```

## Assumptions

- The agent has access to an LLM capable of natural-language plan generation and updating.
- The task can be decomposed into a finite list of rationale slots at the start (tasks with open-ended or dynamically expanding rationale sets are harder to handle).
- Communication is synchronous and turn-based (no concurrent writes to the plan).

## Limitations

- "Fake Solved" hallucinations: agents sometimes mark a rationale as known with "unknown" as the value (4.42% fake-solved rate observed in ablation).
- Plan initialisation quality depends on the LLM's ability to enumerate all required rationales upfront—tasks with hidden information requirements may result in incomplete plans.
- Consensus reasoning is heuristic (discard conflicts) and may incorrectly exclude valid information.

## Tradeoff profile

| Dimension | InfoNav | Baseline (no tracking) |
|---|---|---|
| Communication efficiency | High — focused turns | Low — redundant questions |
| Hallucination rate | Lower | Higher (fake-solved) |
| Plan completeness | LLM-dependent | N/A |
| Overhead | 1 extra LLM call to init plan | None |

## Evaluated by

InformativeBench (NP + Schedule datasets): removing InfoNav drops performance by 15–26 pp on reasoning tasks, with Schedule Hard falling from 12.25% → 7.34% (GPT-3.5).

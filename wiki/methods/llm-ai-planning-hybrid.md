---
name: "LLM–AI Planning Hybrid"
slug: llm-ai-planning-hybrid
aliases:
  - hybrid LLM planner
  - LLM-PDDL hybrid
  - neuro-symbolic planning
tags:
  - llm-agents
  - planning
  - pddl
  - reasoning
  - finance
type: architecture
source_papers:
  - "[[generative-ai-agents-knowledge-work-augmentation]]"
realizes_concepts: []
date_updated: 2026-05-29
---

## Problem setting

Pure LLM-based planning (chain-of-thought, ReAct, Tree of Thoughts) lacks formal guarantees on plan validity and constraint satisfaction. Classical AI planners provide these guarantees but require labor-intensive manual PDDL domain engineering and cannot parse natural language inputs. Knowledge work in regulated, risk-sensitive domains like finance requires both language understanding and constraint-satisfying plans.

## Mechanism

Combines LLMs and classical AI planners (PDDL-based) in a closed-loop hybrid:
1. **Domain model generation**: LLM translates natural language SOPs and documentation into PDDL domain models (actions, preconditions, effects).
2. **State and goal grounding**: LLM maps natural language goals and environment observations into formal PDDL state descriptions.
3. **Planning**: A classical planner (e.g., LAMA, Fast Downward) takes the PDDL domain + problem and returns a valid, optionally optimal plan with formal guarantees.
4. **Execution and replanning**: LLM monitors execution, maps observations back to PDDL states, and triggers replanning on divergence.

## Procedure

1. Parse natural language task description → LLM generates PDDL domain + problem.
2. Validate generated PDDL (optional; open research challenge).
3. Run classical planner → extract action sequence.
4. Execute actions; after each action, LLM interprets environment response → update PDDL state.
5. If goal not reached and replanning triggered → return to step 2 with updated state.

## Assumptions

- The domain can be adequately modeled in PDDL (or a compatible action language).
- LLM has sufficient world knowledge to generate approximately correct domain models from natural language.
- A suitable classical planner is available for the domain type (e.g., propositional, temporal, numeric).

## Limitations

- LLM hallucinations can produce invalid PDDL, breaking planner soundness guarantees.
- Domain model validation remains an open research problem.
- Temporal and numeric reasoning in PDDL is still challenging for complex financial workflows.
- Requires bridging the closed-world assumption of classical planners with the open-world environment of knowledge work.

## Tradeoff profile

- **vs. pure LLM planning**: Gains formal correctness guarantees and constraint handling; loses flexibility for tasks not amenable to PDDL modeling.
- **vs. pure classical planning**: Gains language understanding and knowledge generalization; adds LLM hallucination risk in domain model generation.

## Evaluated by

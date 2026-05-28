---
name: "Tree of Thoughts"
slug: tree-thoughts
type: inference
tags:
  - reasoning
  - planning
  - search
  - llm
  - agentic-ai
source_papers:
  - generative-agentic-ai-survey-conceptualization-challenges
parent_methods: []
child_methods: []
realizes_concepts:
  - chain-thought-reasoning
  - agentic-ai
date_updated: 2026-05-29
---

## Problem setting

Standard chain-of-thought (CoT) prompting generates a single linear reasoning chain, committing to each intermediate step without backtracking. This is suboptimal for complex problems where early mistakes propagate and where exploring alternative solution paths could yield better outcomes.

## Mechanism

Tree of Thoughts (ToT) frames reasoning as a tree search over partial reasoning chains ("thoughts"). At each step, the model generates multiple candidate next thoughts from the current partial chain. These candidates are evaluated — by self-consistency voting, an LLM evaluator, or task-specific heuristics — to estimate their likelihood of leading to a correct solution. The tree is then explored using classical search strategies (depth-first or breadth-first), with pruning applied to discard partial chains with poor evaluations.

A controller maintains the search state, generates prompts for thought expansion, parses model outputs, and ranks candidate next steps. The LLM can serve as both thought generator and evaluator.

Related extensions:
- **Forest of Thoughts (FoT)**: generates variations of the input so that a separate ToT tree is grown for each variant, increasing diversity.
- **Graph of Thoughts (GoT)**: generalizes tree structure to a graph, allowing sub-tasks (nodes) to be merged, scored, and recombined.

## Procedure

1. Initialize: represent the current problem as the root of the tree.
2. Thought expansion: prompt the LLM to generate k candidate continuations (next reasoning steps).
3. Evaluation: score each continuation using self-consistency voting, an LLM-as-judge prompt, or a specialized verifier model.
4. Search step: select the top-scoring continuation(s) to expand next (BFS: expand all above a threshold; DFS: follow the best until terminal or pruned).
5. Prune: terminate branches with scores below a threshold.
6. Repeat until a complete solution is found or budget is exhausted.
7. Return the highest-scoring complete reasoning chain.

## Assumptions

- The LLM can generate meaningful intermediate reasoning steps that can be partially evaluated before the final answer is known.
- Self-consistency voting or LLM-based evaluation provides a useful signal for partial-chain quality.
- The search space is tractable: exponential branching is managed by pruning and depth limits.

## Limitations

- Significantly more expensive than single-pass CoT due to multiple LLM calls per search step.
- LLM-based evaluators can be unreliable for tasks where intermediate correctness is hard to assess.
- Task-specific heuristics for evaluation (when needed) limit generalizability.
- The controller architecture adds engineering complexity beyond a simple prompt.

## Tradeoff profile

| Property | Value |
|---|---|
| Inference cost | High (branching factor × depth × LLM calls) |
| Solution quality | Significantly better than CoT on complex reasoning tasks |
| Generalizability | Moderate — works best when partial solutions can be meaningfully evaluated |
| Implementation complexity | Moderate–High |

## Evaluated by

Evaluated primarily on creative writing, game-of-24 arithmetic reasoning, and miniature crossword puzzles in the original ToT paper. Also discussed in the context of ARC challenge performance for Agentic AI reasoning models.

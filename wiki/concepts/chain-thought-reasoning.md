---
title: "Chain-of-Thought Reasoning"
aliases:
  - CoT
  - chain of thought
  - step-by-step reasoning
  - CoT prompting
tags:
  - reasoning
  - prompting
  - llm
  - agentic-ai
maturity: stable
definition: "A prompting and training paradigm that elicits intermediate reasoning steps from language models before producing a final answer, enabling more accurate and interpretable solutions to multi-step problems."
key_papers:
  - generative-agentic-ai-survey-conceptualization-challenges
first_introduced: "2022"
date_updated: 2026-05-29
related_concepts:
  - agentic-ai
  - retrieval-augmented-generation
---

## Definition

Chain-of-Thought (CoT) reasoning is a technique that induces language models to produce a sequence of intermediate steps — a "reasoning chain" — before arriving at a final answer. It can be triggered by prompting (e.g., "Think step-by-step," few-shot examples with reasoning traces) or instilled via training on data that includes step-wise solutions. CoT was a key step in the evolution from GenAI to Agentic AI: it demonstrated that even single-pass generation could exhibit basic reasoning if structured appropriately, and later evolved into deep reasoning with explicit planning and search in Agentic AI systems.

## Intuition

Rather than treating inference as a single lookup from input to output, CoT decomposes a problem into sub-steps, mirroring how humans write out intermediate work. The model generates each step as part of its output, making the reasoning process visible and allowing downstream steps to condition on earlier ones. Research shows that the *structure* of reasoning chains (logical coherence, validation steps) matters more than the *difficulty* of individual components, and that longer chains (finer decomposition) generally help more than shorter ones — though excessive verbosity is counterproductive.

## Variants

- **Zero-shot CoT**: elicited by appending "Think step-by-step" to the prompt, without demonstrations.
- **Few-shot CoT**: elicited by providing example (problem, reasoning, answer) triples in the prompt.
- **Least-to-most decomposition**: explicitly decomposes the problem into subproblems that are solved sequentially.
- **Hierarchical CoT**: high-level planning at one abstraction level (LLM), low-level execution at another (specialized model or tool).
- **Self-consistency**: samples multiple independent CoT chains and selects the answer by majority vote.
- **Tree of Thoughts (ToT)** / **Forest of Thoughts (FoT)** / **Graph of Thoughts (GoT)**: extends CoT to tree/graph-structured search over multiple reasoning paths with pruning and evaluation.
- **Deep reasoning (Agentic AI)**: CoT is internalized during training (via RL on reasoning traces) and executed automatically without explicit prompting.

## Comparison

CoT prompting was originally a purely prompting-based technique for GenAI; it worked best on math and symbolic reasoning tasks and required users to supply example reasoning paths. Modern Agentic AI systems internalize CoT through training (e.g., DeepSeek-R1 via GRPO reinforcement learning on reasoning trace data), so reasoning is automatic and scales with test-time compute rather than being prompted. The key structural finding is that reasoning chain *structure* (coherence, reflection, validation) dominates over step *content* (exact intermediate answers).

## Known limitations

- Simple CoT primarily helps on math and symbolic reasoning; benefits on language understanding tasks are modest.
- CoT reasoning may not faithfully represent the model's actual decision process (unfaithful reasoning).
- Longer chains can accumulate errors; verbose chains are not always better.
- LLMs may struggle to reflect using simple CoT prompts without external feedback (oracle or compiler output).

## Open problems

- When does CoT reflect genuine reasoning vs. pattern-matching on training data?
- How to efficiently select the "right" level of chain granularity for a given task.
- How to integrate CoT with external symbolic solvers for hybrid reasoning.

## Relationship to foundations

CoT builds on the in-context learning capability of large autoregressive transformer models (GPT-3 era), which can condition on few-shot examples in the prompt and generalize the exhibited pattern to new inputs.

## Realized by

- [[tree-thoughts]]

## My understanding

CoT is arguably the single most impactful prompting discovery in the GenAI era. Its evolution into deep reasoning (test-time compute scaling, RL training on traces) is the core mechanism behind Agentic AI's superior performance on complex tasks.

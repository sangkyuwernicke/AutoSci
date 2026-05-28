---
title: "Agentic AI"
aliases:
  - agentic artificial intelligence
  - LLM agents
  - autonomous AI agents
tags:
  - agentic-ai
  - reasoning
  - llm-agents
  - autonomy
  - generative-ai
maturity: active
definition: "AI systems based on foundation models that can autonomously execute complex, multi-step tasks in dynamic environments through deep reasoning (planning, reflection, search) and interaction with environments, tools, memory, and other agents."
key_papers:
  - generative-agentic-ai-survey-conceptualization-challenges
first_introduced: "2023"
date_updated: 2026-05-29
related_concepts:
  - chain-thought-reasoning
  - retrieval-augmented-generation
  - multi-agent-systems
---

## Definition

Agentic AI refers to AI systems — typically based on large foundation models — that perform tasks by combining two capabilities absent or limited in earlier Generative AI: (i) **deep reasoning** (multi-step, iterative, problem-dependent computation including planning, reflection, and search) and (ii) **interaction** with dynamic environments, tools, external memory stores, other agents, and humans. This allows Agentic AI to pursue complex, long-horizon goals with limited direct supervision, while Generative AI requires detailed per-task instructions and operates in a single-pass response paradigm.

Autonomy levels range from 0 (narrow ML, no initiative) through 1 (assistive/GenAI) to 2–4 (Agentic AI: partial autonomy → goal-oriented collaboration → full autonomous decision-making).

## Intuition

Where a GenAI model is given a prompt and immediately generates a response in one forward pass, an Agentic AI system first decomposes the task, explores multiple sub-plans, executes tool calls and environment interactions, verifies intermediate results, and iterates — analogous to Kahneman's "slow thinking" versus "fast thinking." The key enabler is test-time compute scaling: spending more computation per query to find better solutions.

## Variants

- **Single-agent systems**: a single foundation model with tool access, memory, and a planning loop.
- **Multi-agent systems**: multiple specialized agents with defined roles (personas, goals, tool permissions) that cooperate (or compete) to solve complex tasks.
- **Reasoning models**: models explicitly trained to produce step-by-step reasoning traces (e.g., DeepSeek-R1, OpenAI o1/o3) as a form of internalized planning.
- **World-model agents**: agents that maintain an explicit model of the environment (à la RL world models), enabling simulation-based planning.

## Comparison

| Aspect | Generative AI | Agentic AI |
|---|---|---|
| Reasoning | Immediate single-pass | Iterative planning + reflection |
| Interaction | User only | Tools, environment, other agents, humans |
| Execution | Single-step tasks | Multi-step workflows |
| Adaptability | Bound to training data | Trial-and-error instant learning |
| Autonomy | User-driven | Self-directed (partial to full) |

Agentic AI shows dramatic gains on tasks requiring complex reasoning (e.g., ARC challenge) but only marginal gains over GenAI on factual recall benchmarks (e.g., MMLU), and near-zero performance on real-world browser/computer interaction tasks (WorkArena++).

## Known limitations

- Error accumulation across multi-step reasoning chains.
- Chain-of-thought reasoning may not faithfully reflect the underlying decision process.
- Agentic AI systems are harder to evaluate robustly due to long-horizon, non-deterministic behavior.
- Safety and security risks are amplified: tool invocation, multi-modal attack surfaces, and prompt injection.
- Instant learning remains limited: catastrophic forgetting and adversarial manipulation make persistent parameter updates risky.

## Open problems

- Robust evaluation of long-horizon agentic tasks without oracle ground-truth for intermediate steps.
- Achieving reliable real-world computer/browser interaction (WorkArena++ gap).
- Safe specification of agent goals and constraints that generalize to unforeseen situations.
- Path from current Agentic AI to Artificial General Intelligence (AGI).

## Relationship to foundations

Agentic AI builds on large language models (transformer architecture, next-token prediction pre-training, RLHF post-training) and incorporates concepts from Reinforcement Learning (policy, world model, reward, exploration/exploitation).

## Realized by

- [[tree-thoughts]]

## My understanding

The two-axis framing (reasoning + interaction) is the cleanest decomposition I've seen. The autonomy level taxonomy (0–4) is a useful practical tool for classifying systems and discussing regulatory requirements for human oversight.

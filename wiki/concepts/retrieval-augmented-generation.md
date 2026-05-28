---
title: "Retrieval-Augmented Generation"
aliases:
  - RAG
  - retrieval augmentation
  - knowledge retrieval
tags:
  - memory
  - retrieval
  - llm
  - agentic-ai
  - knowledge-base
maturity: stable
definition: "A technique that augments language model generation by dynamically retrieving relevant context from an external knowledge source (typically a vector database) and prepending it to the model's input."
key_papers:
  - generative-agentic-ai-survey-conceptualization-challenges
first_introduced: "2020"
date_updated: 2026-05-29
related_concepts:
  - agentic-ai
  - chain-thought-reasoning
---

## Definition

Retrieval-Augmented Generation (RAG) addresses a key limitation of standalone language models — their knowledge is frozen at training time and their context window is bounded. RAG systems build an external knowledge store (typically a vector database) by chunking documents, encoding each chunk as a dense vector, and indexing them. At inference time, the user's query is encoded as a vector, used to retrieve the most relevant chunks, and these chunks are prepended to the prompt before generation. This allows the model to incorporate up-to-date, private, or domain-specific knowledge without retraining.

## Intuition

RAG acts as an on-demand long-term memory for language models. Rather than cramming all knowledge into model parameters (expensive, stale) or the context window (limited capacity), RAG maintains a separate indexed store and retrieves only what is relevant to the current query. In the context of Agentic AI, RAG also enables storing and retrieving *agent experiences* (past interactions, observations, reflections), not just static documents — allowing a form of episodic memory.

## Variants

- **Classic RAG** (Lewis et al., 2020): single-stage retrieval of top-k chunks by cosine similarity in embedding space.
- **Adaptive/iterative RAG**: self-reflection-based retrieval where the model decides when additional retrieval is needed (e.g., SELF-RAG).
- **Filtered RAG**: an evaluator classifies retrieved knowledge as correct/incorrect/ambiguous; incorrect knowledge triggers further retrieval.
- **Experience-based RAG**: stores agent action-observation trajectories in the vector DB, optionally processed by an LLM to extract abstract insights.
- **Agentic RAG**: specialized agents for RAG tasks (e.g., SQL-database agents, real-time web retrieval agents).
- **Knowledge graph RAG**: retrieves from knowledge graphs rather than flat vector databases, enabling hierarchical and relational knowledge representation.
- **Full-context (no retrieval)**: for models with very large context windows, all data may be included in the prompt, bypassing retrieval at the cost of higher generation cost.

## Comparison

RAG vs. parametric knowledge (fine-tuning): RAG is more flexible (no retraining for new knowledge), supports private data, and enables real-time updates. Fine-tuning is better for deep domain-specific reasoning. RAG vs. full-context: full-context is simpler and avoids retrieval errors but is only feasible for smaller corpora and incurs high per-query costs. Classical BM25 (keyword-based) retrieval complements vector RAG for exact matches on rare terms.

## Known limitations

- Chunk selection is non-trivial: irrelevant retrieved content occupies context window and can mislead the model.
- Vector retrieval can fail on out-of-vocabulary terms (BM25 complements this).
- Storing and retrieving agent experiences may include irrelevant interaction details.
- Retrieval errors can compound with generation errors.
- Context-only (no retrieval) can outperform RAG for some tasks at the cost of higher latency/cost.

## Open problems

- Optimal chunk granularity and encoding strategy for diverse document types.
- Reliable assessment of retrieved content quality without oracle annotations.
- Integration of structured (relational/graph) and unstructured (vector) retrieval.
- Efficient memory management for very large agent experience stores.

## Relationship to foundations

RAG builds on dense passage retrieval (bi-encoder architectures), vector similarity search (FAISS, HNSW), and standard transformer-based language model generation. In Agentic AI, it connects to the RL concept of memory as a way to store and leverage past experience.

## Realized by

## My understanding

RAG was an early inflection point that enabled GenAI to handle private/fresh data, and in Agentic AI it evolves into a full episodic memory system for agents. The shift from static document retrieval to dynamic experience retrieval is underappreciated but critical for long-horizon autonomous agents.

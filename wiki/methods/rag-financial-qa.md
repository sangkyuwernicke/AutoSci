---
name: "RAG Financial QA"
slug: rag-financial-qa
type: system
tags: [rag, financial-literacy, qa-system, prompt-engineering, dense-retrieval, domain-specific]
source_papers:
  - "[[research-building-system-improve-financial-literacy]]"
parent_methods: []
child_methods: []
realizes_concepts:
  - "[[retrieval-augmented-generation]]"
code_repo: ""
date_updated: 2026-05-29
---

## Problem setting

Domain-specific Q&A for financial literacy education, where grounding LLM responses in authoritative documents is critical to prevent hallucination, and where users have heterogeneous background knowledge requiring adaptive response difficulty.

## Mechanism

A three-stage RAG pipeline:
1. **Embedding + Indexing**: Source documents (Bank of Korea 700 terms, TESAT 70 questions) are chunked and embedded via Ollama Embeddings; vectors are indexed with FAISS.
2. **Dense Retrieval**: User query is embedded with the same model; top-k documents retrieved by cosine similarity over the FAISS index.
3. **Difficulty-adaptive generation**: Query is classified into beginner / intermediate / advanced based on vocabulary density, concept count, sentence length, and reasoning keywords. A role-assigned, source-restricted prompt template (with difficulty-specific directives) and the retrieved documents are fed to Qwen 2.5 for logical generation, then to GPT-4o-mini for learner-friendly reformulation.

## Procedure

1. Preprocess and embed financial corpus.
2. At inference: embed user query → retrieve top-k documents → classify query difficulty → select prompt branch → call Qwen 2.5 → call GPT-4o-mini → return response with optional linked-learning query suggestions.

## Assumptions

- The knowledge base (700 + 70 items) covers the relevant financial concepts for the target user group (Korean 20s).
- Difficulty can be adequately proxied by surface-level linguistic features (vocabulary density, concept count, sentence length).
- Restricting generation to source documents is sufficient for hallucination control.

## Limitations

- Small knowledge base limits coverage; out-of-domain questions are refused.
- No quantitative evaluation of retrieval or generation quality.
- Dual-LLM pipeline (Qwen + GPT-4o-mini) increases latency and API cost.

## Tradeoff profile

High interpretability (grounded in named sources) and hallucination control at the cost of coverage. The difficulty-adaptive branching adds pedagogical value but relies on heuristic classification without empirical validation.

## Evaluated by

Qualitative analysis of three example outputs (beginner, intermediate, advanced) in [[research-building-system-improve-financial-literacy]].

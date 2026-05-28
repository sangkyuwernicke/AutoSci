---
title: "Retrieval-Augmented Generation"
aliases: ["RAG", "retrieval augmented generation", "검색증강생성"]
tags: [rag, llm, information-retrieval, nlp, grounded-generation]
maturity: active
definition: "A framework that enhances LLM generation by first retrieving relevant documents from an external corpus and conditioning the generation on that retrieved context, reducing hallucination and enabling knowledge grounding without full model retraining."
key_papers:
  - "[[research-building-system-improve-financial-literacy]]"
first_introduced: "Lewis et al., 2020 (Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks)"
date_updated: 2026-05-29
related_concepts: []
linked_ideas: []
---

## Definition

Retrieval-Augmented Generation (RAG) combines a retrieval module (which fetches relevant documents from an external knowledge base for a given query) with a generation module (an LLM that produces a response conditioned on both the query and the retrieved documents). The key insight is that factual accuracy and domain specificity can be improved by grounding generation in retrieved evidence rather than relying solely on parametric knowledge baked into model weights.

## Intuition

An LLM trained on general corpora often hallucinates domain-specific or time-sensitive facts. By inserting retrieved passages into the prompt, the model can "look up" factual grounding at inference time — analogous to an open-book exam versus a closed-book exam.

## Variants

- **Sparse retrieval RAG**: Uses TF-IDF or BM25 for retrieval; computationally cheap but misses semantic paraphrases.
- **Dense retrieval RAG**: Uses bi-encoder (e.g., Sentence-BERT, FAISS) for semantic similarity-based retrieval; better coverage of paraphrase variation.
- **Multi-turn RAG**: Maintains conversation history across turns; used in the financial literacy Q&A system described in [[research-building-system-improve-financial-literacy]].
- **Source-restricted RAG**: Prompts instruct the LLM to only use retrieved documents as the information source, refusing out-of-scope queries — used for hallucination control in financial/medical domains.

## Comparison

RAG vs. fine-tuning: Fine-tuning embeds domain knowledge into model parameters (expensive, requires retraining for updates); RAG keeps the LLM frozen and updates the knowledge base independently (flexible, cheaper, more interpretable).

## Known limitations

- Retrieval quality is a hard ceiling: if the relevant document is not retrieved, the answer will be wrong or grounded in irrelevant context.
- Prompt length limits constrain how many retrieved passages can be included.
- Density of retrieved chunks may introduce conflicting or redundant information.
- Latency overhead from retrieval step.

## Open problems

- How to evaluate RAG faithfulness (answers attributable to retrieved documents) vs. standard QA accuracy?
- Optimal chunking and indexing strategies for domain-specific corpora.
- Multi-hop RAG: reasoning across multiple retrieved documents.

## Relationship to foundations

Builds on transformer-based language models and dense passage retrieval (DPR).

## Realized by

- [[rag-financial-qa]]

## My understanding

RAG has become the standard approach for domain-specific LLM deployment where hallucination control and knowledge currency matter. The financial literacy application in [[research-building-system-improve-financial-literacy]] represents a straightforward instantiation: small curated corpus, dense retrieval via FAISS, and source-restricted prompting.

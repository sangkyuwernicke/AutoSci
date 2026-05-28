---
title: "Retrieval-Augmented Generation"
aliases:
  - RAG
  - Retrieval Augmented Generation
  - RAG framework
tags:
  - llm
  - information-retrieval
  - grounding
  - knowledge-augmentation
maturity: active
definition: "A hybrid architecture that augments a pre-trained language model's generation with documents retrieved from an external knowledge base at inference time, improving factual accuracy and enabling real-time knowledge updates without retraining."
key_papers:
  - "[[study-explainable-gpt-based-stock-investment]]"
first_introduced: "Lewis et al., 2020 (NeurIPS)"
date_updated: 2026-05-29
related_concepts: []
linked_ideas: []
---

## Overview

RAG combines a retriever (typically dense-passage or BM25-based) with a generator (LLM) to produce context-grounded outputs. The retriever fetches relevant documents from an external corpus; these are prepended to the LLM prompt as augmented input before generation. This addresses two key LLM limitations: hallucination and stale knowledge (training cutoff).

Two canonical variants: **RAG-Sequence** (one set of retrieved docs per full output) and **RAG-Token** (different docs selected per generated token).

Recent extension: **Agentic RAG** — retrieval and generation are orchestrated by an agent loop that decides when and what to retrieve, enabling multi-hop and iterative reasoning over external sources.

## Key applications

- Open-domain question answering
- Financial analysis with live market data (DART, ECOS, news APIs)
- Medical and legal knowledge retrieval
- Structured output generation (JSON, reports)

## Realized by

- [[role-based-multi-ai-agent-stock]]

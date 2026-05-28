---
title: "GraphRAG Analysis for Financial Narrative Summarization and A Framework for Optimizing Domain Adaptation"
slug: graphrag-analysis-financial-narrative-summarization-framework
arxiv: ""
venue: "FinNLP-FNP-LLMFinLegal @ COLING 2025"
year: 2025
tags: [graphrag, retrieval-augmented-generation, financial-nlp, summarization, domain-adaptation, llm]
importance: 2
date_added: 2026-05-28
source_type: pdf
s2_id: ""
tldr: "GraphRAG underperforms naive RAG on financial narrative summarization but can be improved via an LLM-as-optimizer framework that iteratively refines entity extraction prompts using ground-truth summaries."
contribution_type: [analysis, application]
datasets: [FNS-2023]
code_url: ""
cited_by: []
---

## Problem & Context

Financial narrative summarization requires condensing long annual reports (thousands of words) into structured summaries under 1,000 words. Large language models face two key barriers: (1) context-window limits that prevent processing the full document, and (2) the "lost in the middle" phenomenon where relevant information buried in long contexts is missed. Standard RAG addresses token limits but struggles with global queries that require understanding document-wide themes — a core requirement of query-focused summarization (QFS). GraphRAG was proposed as a remedy by constructing a knowledge graph from source documents and querying it for holistic answers. However, whether GraphRAG's graph-centric view helps or hurts in fact-dense financial domains had not been tested. The field before this paper relied on extractive and abstractive models; GraphRAG's only prior evaluation was on podcast transcripts and news articles.

## Key idea

The paper tests GraphRAG against naive RAG on the FNS 2023 shared task (UK annual reports, ~4,000 documents) and finds that naive RAG is consistently superior. The authors then propose an optimization loop — using an LLM as an optimizer — to iteratively improve GraphRAG's entity-and-relationship extraction prompts by comparing generated summaries against gold summaries. The optimizer LLM identifies missing entities and relationships, analyzes errors against four quality objectives (comprehensiveness, directness, completeness, conciseness), and generates revised prompt instructions. This closes part of the performance gap by expanding and refining the entity type list used during graph indexing.

## Method

**Naive RAG baseline**: Fixed-size chunking (chunk size 1,200, overlap 100), cosine-similarity retrieval via ChromaDB, Mistral-7B as generator.

**Default GraphRAG**: LLM-guided knowledge graph construction; entity and relationship extraction, summarization, and community report generation; uses globally summarized graph nodes for query answering.

**Optimized domain adaptation**: Extends GraphRAG's auto-tuning (which uses domain knowledge + persona to produce entity extraction prompts) with an iterative optimization loop. The optimizer LLM (Llama-3.1-405B) receives `<generated_summary, gold_summary>` pairs, identifies extraction errors, and outputs refined `ENTITY_TYPES_PROMPT` instructions. This runs for multiple iterations until prompt quality stabilizes. A separate judge LLM (Cohere Command R+) evaluates summaries using four metrics: comprehensiveness, directness, completeness, conciseness.

**Evaluation**: FNS 2023 English validation set (413 reports). DiMSum used for narrative section identification prior to summarization.

## Experiment & Results

| Approach | Comprehensiveness | Directness | Completeness | Conciseness |
|---|---|---|---|---|
| Default GraphRAG | 57.66 | 67.48 | 5.99 | 18.57 |
| Naive RAG | **79.81** | **79.79** | **27.18** | **49.53** |
| GraphRAG Domain Adaptation | 67.81 | 79.69 | 10.43 | 26.06 |
| Optimized Domain Adaptation | 75.45 | **83.17** | 10.04 | 24.00 |

Key findings: (1) Naive RAG beats default GraphRAG by large margins on all four metrics. (2) GraphRAG's standard auto-tuning partially recovers comprehensiveness and directness but completeness and conciseness remain far below naive RAG. (3) The proposed LLM-optimizer further improves comprehensiveness (67.81 → 75.45) and directness (79.69 → 83.17), but completeness and conciseness remain below naive RAG levels. The qualitative analysis shows GraphRAG drifts toward thematic/employee narratives and hallucinated community contexts rather than concrete financial figures.

## Limitations

- Optimized GraphRAG still underperforms naive RAG on completeness and conciseness despite iterative tuning.
- Experiments use open-source models (Mistral-7B, Llama-3.1-405B) as substitutes for intended OpenAI models, which may limit generalizability of GraphRAG's performance to original implementation.
- No analysis of the accuracy of the extracted knowledge graph itself (entity precision/recall vs. ground truth).
- Graph structure is fixed after indexing; subgraph selection per query is not explored.
- Evaluation is limited to the English FNS 2023 subset; no multilingual or out-of-domain validation.

## Open questions

- Would thematic subgraph construction (e.g., per revenue theme or strategic theme) recover the completeness gap?
- Can the optimizer be applied to the graph structure itself (not just entity type prompts)?
- Does GraphRAG's global-context advantage materialize for different QFS tasks where cross-document synthesis matters more than fact retrieval?
- How does performance scale with better base models (GPT-4o class) for entity extraction?

## My take

This is a careful empirical study that surfaces a real failure mode of GraphRAG in fact-dense domains: the community-level summarization trades precision for breadth, which is the wrong trade-off when financial metrics matter. The proposed optimization framework is lightweight and practically motivated, though it does not close the gap fully. The paper's value is primarily diagnostic — it is the first systematic GraphRAG evaluation on FNS and its findings should temper enthusiasm for graph-based RAG in structured financial reporting tasks. The method page for the LLM-optimizer-based domain adaptation is separately captured.

## Related

- [[graphrag]] — central concept being analyzed and extended
- [[llm-optimizer-domain-adaptation]] — method proposed by this paper

---
title: "GraphRAG"
aliases: ["Graph RAG", "graph-based retrieval-augmented generation", "graph RAG"]
tags: [retrieval-augmented-generation, knowledge-graph, summarization, llm, nlp]
maturity: active
definition: "A retrieval-augmented generation approach that constructs a global knowledge graph from source documents using an LLM, then uses the graph's entity and community structures to answer queries with broad contextual understanding — in contrast to naive RAG which retrieves flat text chunks."
key_papers: [graphrag-analysis-financial-narrative-summarization-framework]
first_introduced: "Edge et al., 2024 (From Local to Global: A Graph RAG Approach to Query-Focused Summarization)"
date_updated: 2026-05-28
related_concepts: []
linked_ideas: []
---

## Definition

GraphRAG is a retrieval-augmented generation paradigm that first indexes a document corpus by guiding an LLM through source content to extract entities and relationships, forming a knowledge graph. The graph is organized into communities (clusters of related entities), and for each query, relevant community summaries are retrieved instead of raw text chunks. This gives GraphRAG a globally coherent view of the corpus, enabling answers to broad thematic queries such as "What are the main themes across all documents?"

The indexing pipeline includes: (A) entity and relationship extraction, (B) entity and relationship summarization to merge duplicate instances, and (C) community report generation — summaries for each graph cluster. At query time, the appropriate community summaries form the context for the generator LLM.

## Intuition

Standard RAG retrieves local text snippets — good for specific lookups but poor for queries that require integrating information across many documents. GraphRAG encodes global structure into the retrieval index, making it better suited to summarization tasks where document-wide understanding matters. The cost is that graph construction introduces an intermediate representation layer that may distort or omit fine-grained numeric facts.

## Variants

- **Default GraphRAG**: Uses domain knowledge + persona prompting for entity type identification during indexing.
- **Domain-adapted GraphRAG**: Extends default with automated prompt tuning via LLM-generated entity type prompts specific to the target domain.
- **Optimized GraphRAG (Shukla et al., 2025)**: Further extends domain adaptation using an iterative LLM-as-optimizer loop over entity extraction prompts, guided by comparison between generated and gold summaries.

## Comparison

GraphRAG vs. Naive RAG on the FNS 2023 financial narratives task (Shukla et al., 2025): Naive RAG outperforms GraphRAG on all four quality metrics (comprehensiveness 79.81 vs 57.66, directness 79.79 vs 67.48, completeness 27.18 vs 5.99, conciseness 49.53 vs 18.57). GraphRAG's community-level summarization can introduce thematic drift and hallucinated entity contexts, which harms precision in fact-dense financial domains.

## Known limitations

- Community summarization trades fact precision for thematic breadth, which is harmful in data-intensive domains like finance.
- Performance is sensitive to the quality of entity type definitions used during indexing; the default auto-tuning may miss domain-critical entity types.
- Computationally expensive compared to naive RAG due to graph construction overhead.
- Designed for Microsoft/OpenAI model stack; open-source substitutions may reduce performance further.

## Open problems

- How to construct thematic subgraphs (e.g., revenue variation graph) that better align with the query intent?
- Can graph structure quality (entity accuracy) be evaluated automatically and used to guide indexing improvements?
- What domains actually benefit from GraphRAG's global structure over naive RAG's direct retrieval?

## Relationship to foundations

GraphRAG is grounded in knowledge graph construction, community detection (graph clustering), and retrieval-augmented generation. The LLM-as-graph-builder role connects it to LLM-as-annotator and information extraction traditions.

## Realized by

- [[llm-optimizer-domain-adaptation]]

## My understanding

GraphRAG's value proposition — global context via knowledge graphs — is compelling for open-domain question answering but appears to hurt performance in fact-extraction tasks where specific numeric entities must be retrieved accurately. The community-level abstraction layer introduces a lossy compression that is appropriate for thematic understanding but not for financial reporting, where exact figures matter.

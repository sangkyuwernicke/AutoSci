---
name: "LLM-as-Optimizer for GraphRAG Domain Adaptation"
slug: llm-optimizer-domain-adaptation
type: prompting
tags: [graphrag, domain-adaptation, llm, optimization, entity-extraction, summarization]
source_papers: [graphrag-analysis-financial-narrative-summarization-framework]
parent_methods: []
child_methods: []
realizes_concepts: [graphrag]
code_repo: ""
date_updated: 2026-05-28
---

## Problem setting

GraphRAG's indexing quality depends on the entity types defined during the extraction phase. Default auto-tuning uses domain knowledge and persona prompting, but this static strategy cannot accommodate the intricate relationships and domain-specific entity nuances in fact-dense corpora like financial reports. The problem is to automatically discover and refine the right entity vocabulary for a target domain without manual prompt engineering.

## Mechanism

The method introduces an iterative optimizer LLM loop on top of GraphRAG's standard domain adaptation pipeline:

1. **Generator LLM** produces summaries from `<report chunks, ground summaries>` using the current entity extraction prompt.
2. **Optimizer LLM** (Llama-3.1-405B) receives `<generated_summary, gold_summary>` pairs and performs:
   - **Comparison & error identification**: identify missing entities, relationships, or facts relative to the gold summary.
   - **Objective analysis**: analyze errors against four objectives — comprehensiveness, directness, completeness, conciseness.
   - **Instruction generation**: produce revised instructions for the `ENTITY_TYPES_PROMPT` to improve extraction in the next iteration.
3. The refined entity type list is fed back into the GraphRAG indexing pipeline for the next iteration.

The optimizer prompt is a structured three-part instruction: compare `GENERATED_SUMMARY` to `GOLDEN_SUMMARY`, determine why entities/relationships were missed, and modify `ENTITY_TYPES_PROMPT` based on the specified optimization metrics.

## Procedure

1. Run GraphRAG's standard auto-tuning to get an initial domain-adapted entity extraction prompt.
2. Run the Generator LLM on a sample of source documents to produce summaries.
3. Feed `(generated summary, gold summary)` pairs to the Optimizer LLM with the structured three-part prompt.
4. Collect the Optimizer's suggested entity type refinements.
5. Reconstruct the entity extraction prompt with the enriched entity type list.
6. Re-run GraphRAG indexing with the new prompt.
7. Repeat steps 2–6 until convergence.

## Assumptions

- High-quality gold summaries are available for a training split (requires annotated data).
- The optimizer LLM has sufficient capacity to compare summaries and diagnose extraction gaps (Llama-3.1-405B used in the paper).
- Entity-level improvements in the extraction prompt translate to better graph coverage and thereby better summaries.

## Limitations

- Requires ground-truth summaries for the optimization loop — not applicable in fully unsupervised settings.
- Improvements in comprehensiveness and directness do not fully recover completeness or conciseness gaps vs. naive RAG.
- Each iteration requires re-indexing the graph, which is computationally expensive for large corpora.
- Entity type list expansion may introduce noise if the optimizer over-generalizes.

## Tradeoff profile

- **Accuracy vs. compute**: More iterations improve entity coverage but multiply graph construction cost.
- **Recall vs. precision**: Expanding entity types improves comprehensiveness (recall-like) but may reduce conciseness (precision-like) by adding tangential entities.
- **Generalization**: Tuned entity types are corpus-specific; re-tuning needed for new domains.

## Evaluated by

Evaluated on FNS 2023 English validation set using four LLM-judge metrics (comprehensiveness, directness, completeness, conciseness). Results in Shukla et al. (2025): optimized domain adaptation achieves 75.45 comprehensiveness and 83.17 directness, vs. 67.81 and 79.69 for standard domain adaptation, but still below naive RAG (79.81, 79.79).

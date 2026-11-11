---
title: "Research on Building a Q&A System to Improve Financial Literacy Using RAG"
slug: research-building-system-improve-financial-literacy
arxiv: ""
venue: "Information Systems Review (경영정보학연구)"
year: 2025
tags: [rag, financial-literacy, qa-system, llm, prompt-engineering, nlp, domain-specific-qa]
importance: 2
date_added: 2026-05-29
source_type: pdf
s2_id: ""
tldr: "A RAG-based Q&A system using Bank of Korea financial terminology and TESAT exam questions delivers adaptive, difficulty-tiered financial literacy education for Korean youth."
contribution_type: [system, application]
datasets: ["Bank of Korea Economic and Financial Terms 700", "TESAT Key Questions 70"]
code_url: ""
cited_by: []
---

## Problem & Context

Financial literacy among Korean young adults (ages 20–30) is persistently low despite high digital literacy. A 2022 OECD survey found Korea scored below average on financial attitudes, and the Korean Ministry of Economy and Finance's 2023 nationwide survey found an average score of 58.7/100 — below the passing threshold. Youth bankruptcy filings are rising, and 90% of survey respondents acknowledged the need for improved financial education.

Existing financial education relied on static textbooks and traditional pedagogical formats that cannot respond to learner-initiated questions in real time. Prior academic work analyzed correlations between financial knowledge, attitudes, and behaviors, but did not provide interactive, personalized Q&A systems. The gap this paper targets: a real-time, personalized, retrieval-grounded financial education system.

## Key idea

Apply Retrieval-Augmented Generation (RAG) to financial literacy education by grounding an LLM's responses in a curated, authoritative corpus (Bank of Korea terminology + TESAT exam questions). Crucially, the system segments responses by difficulty level — beginner, intermediate, advanced — determined from the linguistic complexity of the user's query, and employs prompt engineering to enforce the role of "economics teacher" while restricting responses to source-document content to suppress hallucinations.

## Method

**Architecture overview:**
1. **Document embedding and indexing**: Financial terms and TESAT questions are preprocessed, then embedded using Ollama Embeddings into dense vectors and indexed with FAISS (Facebook AI Similarity Search) for efficient nearest-neighbor lookup.
2. **Retrieval (dense retriever)**: User queries are embedded with the same model; top-k documents are retrieved by cosine similarity. A dense retrieval approach (semantic rather than keyword matching) is used.
3. **Generation**: Retrieved documents are inserted into a prompt template and fed to Qwen 2.5 (primary LLM for logical, coherent answers) followed by GPT-4o-mini (reformulation into learner-friendly language).

**Prompt engineering design:**
- Role assignment: "You are an economics teacher."
- Source restriction: All answers must be grounded in the two source documents; unknown questions receive "I cannot answer this question."
- Difficulty-adaptive branching: Query difficulty is classified into beginner / intermediate / advanced based on vocabulary density, number of concepts, sentence length, and presence of reasoning indicators (e.g., "why", "reason"). Each tier receives tailored prompt directives.

**Datasets:**
- *Bank of Korea Economic and Financial Terms 700* (발간 2018): Authoritative lexicon covering monetary policy, financial markets, macroeconomics, etc. Each entry includes concept background, meaning, and application cases.
- *TESAT Key Questions 70*: Government-certified economic competency exam (Korea Economic Daily, certified 2010). Five-choice format covering foundational economics through contemporary policy.

## Experiment & Results

The paper presents qualitative analysis of system outputs across the three difficulty tiers rather than quantitative benchmarks:

- **Beginner example** — Query: "Why is it hard to get a loan when interest rates rise?" System correctly identified the two core concepts (interest rate, loan), classified as beginner, and generated a causal explanation (rate rise → interest cost increase → reduced loan demand + tighter bank lending standards) using plain language.
- **Intermediate example** — Query about fiscal policy during COVID-19. System integrated multiple concepts (fiscal policy, liquidity, inflation, economic stimulus), provided a balanced account of short-term recovery effects and long-term inflation risk, citing the liquidity trap mechanism.
- **Advanced example** — Query about why countries with high debt (like Japan) do not face economic crises. System synthesized: domestic bond holding structure, low-interest-rate policy management, central-bank QE, industrial stability, and social trust — a multi-factor causal analysis.

No quantitative metrics (accuracy, hallucination rate, BLEU, ROUGE, user satisfaction) are reported. The paper acknowledges this as a limitation and states that a baseline comparison against non-RAG models is planned for future work.

## Limitations

1. The knowledge base (700 terms + 70 TESAT questions) may not cover the full scope of real-world financial decision-making scenarios.
2. No quantitative evaluation: no numeric metrics for accuracy, hallucination rate, or user satisfaction are provided.
3. The system targets 20s-aged Korean youth; generalizability to other age groups and other languages is untested.
4. Long-term impact on actual financial decision-making behavior is not assessed.
5. The RAG system's superiority over baseline LLM responses is asserted but not empirically demonstrated.

## Open questions

- How does RAG grounding compare to a vanilla ChatGPT baseline on Korean financial Q&A accuracy and hallucination rate?
- Can the difficulty-classification heuristic (vocabulary density, concept count, sentence length) be validated against human-rated difficulty labels?
- Would a fine-tuned domain LLM outperform the RAG + general LLM combination for this task?
- How does the system perform on out-of-domain financial questions not covered by the two source documents?

## My take

A clean application paper that demonstrates a sensible RAG pipeline for domain-specific financial education in the Korean context. The prompt-based difficulty-adaptive response generation is practically motivated and easy to replicate. However, the absence of quantitative evaluation is a significant weakness — the paper reads as a system description rather than an empirical study. The use of Qwen 2.5 + GPT-4o-mini in tandem (reasoning then reformulation) is an interesting design choice worth noting for education-domain QA pipelines. The linked-learning (search query recommendation) feature is mentioned in the abstract but not elaborated in the methodology section.

## Related

- [[retrieval-augmented-generation]] — core technique
- [[financial-literacy]] — application domain
- [[prompt-engineering]] — key design component
- [[rag-financial-qa]] — method entity

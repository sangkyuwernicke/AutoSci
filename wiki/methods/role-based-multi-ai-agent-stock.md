---
name: "Role-Based Multi-AI Agent Stock Analysis"
slug: role-based-multi-ai-agent-stock
type: system
tags:
  - financial-ai
  - multi-agent-systems
  - llm-agents
  - prompt-engineering
  - stock-analysis
  - retrieval-augmented-generation
source_papers:
  - "[[study-explainable-gpt-based-stock-investment]]"
parent_methods: []
child_methods: []
realizes_concepts:
  - "[[retrieval-augmented-generation]]"
code_repo: ""
date_updated: 2026-05-29
---

## Description

A system design pattern for automated investment analysis using a single LLM backbone (GPT-4o) with eleven role-specialized agents implemented via persona-based prompt engineering. Each agent is activated in sequence by the Planning agent's workflow and operates on retrieved external data (DART, ECOS, Google News/Finance APIs via OpenAPI 3.1.0). The final Reflection agent applies self-refinement (self-feedback + iterative improvement) twice before producing the output report.

## Agent roles

1. **Planning Agent** — designs and structures the analysis pipeline
2. **DART Agent** — retrieves corporate disclosure filings via DART OpenAPI
3. **SearchEngine Agent** — real-time news, ESG, industry trends via SerpAPI/Google
4. **ECOS Agent** — macroeconomic indicators from Bank of Korea API
5. **Fundamental Agent** — intrinsic value, industry competitiveness, ESG evaluation
6. **Finance Agent** — financial ratios (ROE, ROA, PER, PBR, debt ratio, etc.)
7. **Chart Agent** — technical analysis: trend lines, RSI, MACD (1-month window)
8. **Machine Learning Agent** — price forecasting with RF, XGBoost, SVM, ARIMA; evaluated by MAE/RMSE/MAPE
9. **Reasoning Agent** — provides intermediate investment opinions per stage
10. **Analysis Agent** — integrates all stage outputs and investment opinions
11. **Reflection Agent** — self-refines the integrated report twice; generates final .docx

## RAG integration

All agents operate under a RAG architecture: each API agent retrieves live external data and augments the LLM's context before generation. This reduces hallucination and ensures real-time information currency.

## Realized concepts

- [[retrieval-augmented-generation]]

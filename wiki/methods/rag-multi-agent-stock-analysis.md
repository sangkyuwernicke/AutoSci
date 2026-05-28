---
name: "RAG Multi-Agent Stock Analysis"
slug: rag-multi-agent-stock-analysis
type: system
tags:
  - financial-ai
  - multi-agent-systems
  - retrieval-augmented-generation
  - stock-analysis
  - llm-application
source_papers:
  - "[[study-explainable-gpt-based-stock-investment]]"
parent_methods: []
child_methods: []
realizes_concepts:
  - "[[explainable-ai-stock-investment-analysis]]"
code_repo: ""
date_updated: "2026-05-29"
---

## Problem setting

Automated stock investment analysis requires integrating heterogeneous real-time data sources (financial disclosures, macroeconomic statistics, news, price data) and applying multiple analytical methods (fundamental analysis, technical analysis, ML forecasting) in a structured workflow — while producing interpretable, natural-language investment reports accessible to non-expert investors.

## Mechanism

The method combines three components:

1. **RAG (Retrieval-Augmented Generation)**: A ChatGPT-4o instance retrieves real-time external documents from DART (Korean electronic disclosure API), Bank of Korea ECOS (economic statistics API), and Google News & Finance (via SerpAPI). Retrieved content is injected into each agent's prompt context as augmented input, grounding LLM outputs in current factual data and reducing hallucination.

2. **Role-based multi-agent decomposition via prompt engineering**: Eleven agents are implemented as prompt personas within a single GPT-4o model. Each agent is responsible for a distinct analysis stage: Planning → API data collection (DART, ECOS, SearchEngine) → Fundamental → Finance → Chart → Machine Learning → Reasoning → Analysis → Reflection. Agents operate sequentially; each stage's output feeds the next.

3. **Self-refinement loop**: The Reflection Agent performs two rounds of self-review (self-refine) on the assembled draft report, checking for internal consistency and coverage against the original plan before finalizing.

## Procedure

1. User inputs company name or KRX ticker code
2. Planning Agent generates an 8-step analysis plan; user reviews and approves (or requests revisions)
3. API Agents (DART, ECOS, SearchEngine) collect real-time data in parallel
4. Domain agents (Fundamental, Finance, Chart, ML) execute their respective analysis modules; Reasoning Agent provides intermediate opinions at each stage
5. Analysis Agent consolidates all stage outputs and derives investment recommendation
6. Reflection Agent runs 2 self-refinement cycles on the full report
7. Final investment report is exported as a .docx file named `{Company}_AI_Agent_Stock_Investment_Report.docx`

Machine learning models used by ML Agent: Random Forest, XGBoost, SVM (SVC), ARIMA. Evaluation metrics: MAE, RMSE, MAPE. Output includes buy/hold/sell signal per model.

## Assumptions

- Single LLM model (GPT-4o) can faithfully simulate role-isolated agents via prompt engineering alone
- 1-month historical price/volume data is sufficient for short-term (5-day) ML forecasting
- DART, ECOS, and SerpAPI data quality is sufficient for professional-grade analysis
- Sequential agent execution (without parallelism) is adequate for the latency requirements of stock analysis

## Limitations

- Prompt-based role separation does not provide true computational isolation — the model may blend agent behaviors under long contexts
- Memory and execution-time constraints of ChatGPT Plus can cause stage skipping in extended analyses
- ML models trained on 1-month windows generalize poorly to medium/long-term price trends
- DART API returns summarized (not full) financial statements due to memory overflow constraints
- System is tightly coupled to Korean-market data APIs; international adaptation requires significant re-engineering

## Tradeoff profile

| Dimension | Value |
|---|---|
| Interpretability | High — natural language report at each stage |
| Automation | High — full pipeline from ticker input to report |
| Data freshness | High — real-time API calls |
| ML accuracy | Moderate — short training window, no deep-learning models |
| Computational cost | Low (single GPT Plus subscription) |
| Scalability | Low — sequential, single-model, API rate-limited |

## Evaluated by

Demonstrated on Lotte Chemical (KRX: 011170); qualitative evaluation only — no quantitative comparison to baseline systems or human analyst recommendations.

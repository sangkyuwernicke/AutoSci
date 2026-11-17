---
title: "A Study on an Explainable GPT-Based Stock Investment Analysis System: Integrated Design of RAG Structure and Multi-AI Agent Framework"
slug: study-explainable-gpt-based-stock-investment
arxiv: ""
venue: "Information Systems Review (경영정보학연구)"
year: 2025
tags:
  - financial-ai
  - multi-agent-systems
  - retrieval-augmented-generation
  - explainability
  - stock-analysis
  - llm-application
importance: 3
date_added: "2026-05-29"
source_type: pdf
s2_id: ""
tldr: "An automated, explainable stock investment analysis system built with ChatGPT-4o, 11 role-based AI agents, and a RAG framework that integrates real-time financial APIs to generate structured investment reports."
contribution_type:
  - system
  - application
datasets: []
code_url: ""
cited_by: []
---

## Problem & Context

Individual investors in the Korean stock market face growing information asymmetry and analytic complexity, while existing AI-based tools remain siloed — covering only subsets such as news sentiment analysis, technical charting, or financial ratio prediction. Prior work (MarketSenseAI 2.0, FinRobot, GPT-InvestAR, TradingAgents) demonstrates that LLM-based agents can match professional analysts in narrow tasks, but no system had realized a fully integrated, end-to-end automated investment workflow covering financial disclosures, macroeconomic indicators, ESG data, technical analysis, and machine-learning price forecasting in a single unified pipeline. Black-box ML models further undermine practical adoption by limiting interpretability. The paper targets the Korean domestic market specifically, integrating DART (Korea's SEC-equivalent electronic disclosure system) and ECOS (Bank of Korea economic statistics) as primary data sources.

## Key idea

The central insight is that combining RAG (for real-time factual grounding) with a role-partitioned multi-agent architecture (for workflow specialization) inside a single ChatGPT-4o GPT custom instance can automate the entire investment analysis lifecycle — from planning through final report — while remaining interpretable via natural-language outputs. Each agent is implemented via prompt engineering personas within a single LLM, avoiding multi-model orchestration complexity. The system follows a strict 8-stage sequential pipeline gated by user approval before execution begins.

## Method

The system is implemented as a ChatGPT Plus GPT custom agent. The architecture has three orthogonal components:

1. **RAG layer**: Real-time external retrieval from DART OpenAPI (financial disclosures), Bank of Korea ECOS API (macroeconomic indicators), and Google News & Finance via SerpAPI. Retrieved documents are injected as augmentation context, reducing hallucination and enabling up-to-date analysis.

2. **Multi-agent structure (11 agents)**: All agents are prompt-engineering personas within a single GPT-4o model:
   - *Planning Agent* — structures the 8-step analysis plan and requests user approval
   - *Dart Agent*, *Ecos Agent*, *SearchEngine Agent* — API data collection roles
   - *Fundamental Agent* — intrinsic value and industry competitiveness
   - *Finance Agent* — financial ratio analysis (ROE, ROA, PER, PBR, etc.)
   - *Chart Agent* — technical analysis (RSI, MACD, trend lines) on 1-month price/volume data
   - *Machine Learning Agent* — price forecasting with RF, XGBoost, SVM, ARIMA; evaluated by MAE, RMSE, MAPE; outputs buy/hold/sell signals
   - *Reasoning Agent* — intermediate opinion synthesis at each stage
   - *Analysis Agent* — cross-stage synthesis and final investment opinion
   - *Reflection Agent* — self-refinement via 2 rounds of self-feedback, producing final report

3. **GPT Instruction schema**: Four-part instruction block (Definitions & Procedures, AI Agents, API connection rules, Display Rules) encoded in GPT's system instruction; knowledge base includes corp_code.xlsx, guide.docx, and NanumGothic.ttf for Korean font rendering.

The system generates Python code internally (executed via GPT's code interpreter) for ML model training and chart visualization; code can also be exported and verified in external Jupyter environments.

## Experiment & Results

Applied to Lotte Chemical (KRX: 011170) as a demonstration case. The full 8-stage pipeline executed end-to-end:

- **DART API**: 3-year (2022–2024) consolidated financials retrieved; Lotte Chemical showed 3 consecutive years of operating losses (−76.2B, −34.7B, −89.4B KRW) and 2024 net loss of −1.8T KRW
- **ECOS**: Macroeconomic snapshot (base rate 2.5%, GDP growth −0.2%, Dubai crude $63.6)
- **ML price forecasting** (1-month training data, 5-day forward prediction):
  - Random Forest: MAE ≈ 968 KRW, RMSE ≈ 1,087 KRW, predicted 63,800 KRW
  - XGBoost: MAE ≈ 975, RMSE ≈ 1,091, predicted 63,700 KRW
  - ARIMA: MAE ≈ 1,145, RMSE ≈ 1,285, predicted 63,300 KRW (least accurate)
- **Technical analysis**: RSI in neutral zone (45–65), MACD converging, suggesting short-term range-bound trading near 62,000–65,000 KRW
- **Final verdict**: Hold — fundamental weakness (ongoing losses) offsets long-term turnaround potential via ESG/green chemistry transition
- **Reproducibility**: Confirmed — repeated runs with same stock code yielded consistent analysis given the same API data snapshot

No benchmark comparison against other automated systems or human analysts was conducted; evaluation is qualitative and demonstration-style.

## Limitations

1. **Single-model multi-agent**: All agents run inside one GPT-4o model, so role separation is via prompt framing alone — no true isolation, parallelism, or cross-agent verification
2. **Context/memory constraints**: In long analyses, GPT intermittently skips planned stages; mitigated by Planning–Analysis cross-check prompt, but not fully eliminated
3. **Short training window for ML**: All models trained on 1-month data only; inadequate for medium/long-term trend prediction (ARIMA explicitly underperforms on sharp price swings)
4. **API limitations**: DART API memory overflow on full financial statements (summary only used); Google Finance limited to 1-month historical data; SerpAPI depends on commercial subscription
5. **Domain generalization**: System tuned for Korean market data sources (DART, ECOS, KRX codes); re-adaptation required for other markets
6. **No human-expert baseline**: Results not compared against professional analyst reports or alternative AI systems in quantitative terms
7. **ChatGPT Plus resource limits**: Response delays and task omissions occur under peak load; LSTM/GRU models not usable due to missing Python library support in GPT environment

## Open questions

- Can multi-model agent orchestration (e.g., domain-specialized open-source LLMs via Hugging Face) replace prompt-persona design to achieve true role isolation and improved domain expertise?
- What is the optimal training window and model architecture for short-to-medium-term Korean stock price forecasting when data is limited to API-accessible history?
- How does this system's investment recommendations compare to professional analyst recommendations and market-beating benchmarks (Sortino ratio, alpha vs. KOSPI)?
- Can agentic RAG with longer context windows (GPT-4o+ successors) eliminate stage-skipping failures?

## My take

This paper is primarily an engineering/application demonstration rather than a scientific contribution. The 11-agent design is architecturally interesting as a structured prompt-engineering pattern, but the evaluation is anecdotal — one stock, no baselines, qualitative verdict only. The system's real value is in showing that a non-programmer investor could in principle trigger a full multi-source financial analysis with a single company name input. The approach of combining RAG-based real-time retrieval with ML-based quantitative signals and LLM-based explanation is a reasonable practical architecture. The Korean market focus (DART, ECOS) fills a gap in English-language research that mostly covers SEC/US markets.

## Related

- [[marketsense-ai-2]] — RAG + LLM agents for S&P 500 stock analysis; achieves 33.8% higher Sortino ratio vs. market
- [[trading-agents]] — role-separated LLM trading agents (fundamental analyst, sentiment analyst, trader roles)
- [[finrobot]] — CoT-based multi-agent for equity research and investment report generation
- [[gpt-investar]] — GPT-based annual report analysis for stock investment with backtesting
- [[investlm]] — finance-domain fine-tuned LLM for investment advisory

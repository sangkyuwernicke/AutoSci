---
title: "ETF Asset Allocation Strategy Using ChatGPT and Chain-of-Thought Prompting"
slug: etf-asset-allocation-strategy-using-chatgpt
arxiv: ""
venue: "Information Systems Review (경영정보학연구)"
year: 2025
tags:
  - llm
  - finance
  - portfolio-management
  - chain-of-thought
  - etf
  - sentiment-analysis
  - robo-advisor
importance: 2
date_added: 2026-05-29
source_type: pdf
s2_id: ""
tldr: "A two-stage CoT prompting framework uses ChatGPT to extract sector-level signals from ~94k Korean news headlines and derive ETF portfolio weights that outperform KOSPI 200 and domestic AI-managed ETFs."
contribution_type:
  - method
  - application
datasets:
  - Korean economic news headlines (93,967 articles, H1 2024)
  - KODEX sector ETFs (KRX)
code_url: ""
cited_by: []
---

## Problem & Context

Traditional quantitative portfolio methods (Markowitz mean-variance, Black-Litterman) rely on numeric data and struggle to incorporate unstructured textual information such as news. Robo-advisors in Korea have shown mixed performance: some outperform active funds, others trail KOSPI 200. Meanwhile, news-driven sentiment analysis had been limited to rule-based lexicons, SVMs, and BERT-class models with short input windows and no generation capability. The field lacked a systematic framework for chaining LLM-based text understanding directly into investable ETF weights.

## Key idea

Use GPT-4o-mini with Chain-of-Thought (CoT) prompting in a two-stage pipeline to transform raw Korean economic news headlines into sector ETF allocation weights. Stage 1 (Task1) extracts the top-30 keywords by frequency/importance and maps each to one of 11 predefined KRX sector categories. Stage 2 (Task2) converts the sector signal summary into portfolio weights summing to 100%, with explicit JSON-structured reasoning. Repeating this 20 times per dataset and averaging reduces the non-deterministic variance of LLM outputs.

## Method

**Two-stage CoT ETF Allocation Framework**

1. **Data collection**: 93,967 Korean economic news headlines scraped from Maeil Kyungjae, Korea Economic Daily, and Money Today (Selenium), January–June 2024. Articles with irrelevant tags ([사진], [연예]) removed; data grouped into 1-week, 2-week, 4-week windows. 4-week batches are randomly sampled down to 3,000 rows to fit GPT API token limits.

2. **Task1 prompt (keyword extraction + sector mapping)**: Input is a batch of headlines. Output is a structured JSON array of 30 keywords, each with `keyword`, `sector` (one of 11 fixed categories), `frequency`, and `detail` fields. CoT is enforced by requiring the model to state the sector's direction, intensity, recurrence, and contextual coherence before assigning a weight.

3. **Task2 prompt (weight generation)**: Input is the Task1 output. Output is a JSON object with `sector_allocations` (sector, allocation %, reason) and an overall `investment_strategy`. Constraints: allocations sum to 100%, no negative weights, reasons cite 2–3 sentences from Task1 keywords.

4. **Investment universe**: 10 KODEX sector ETFs (semiconductor, banking, auto, machinery, energy-chemicals, steel, transport, media, IT, consumer staples) plus 3 domestic AI-managed ETFs as benchmarks.

5. **Rebalancing schedules**: Three strategies (1-week, 2-week, 4-week) applied independently.

6. **Robustness**: Each text batch is run 20 times; the mean allocation vector is used for backtesting. The ±2 standard-deviation band is reported.

7. **Performance metrics**: Annualized expected return, volatility (standard deviation), Sharpe ratio (risk-free rate = 3.55% Korean CD rate), and maximum drawdown (MDD). Prices from Yahoo Finance API.

## Experiment & Results

**Backtest period**: 2024-01-29 to 2024-06-17 on Korean market data.

| Portfolio | Return | Volatility | Sharpe | MDD |
|---|---|---|---|---|
| 1-week GPT | 38.23% | 9.82% | 3.53 | -4.69% |
| 2-week GPT | 37.64% | 11.81% | 2.88 | -3.82% |
| 4-week GPT | 40.96% | 13.56% | 2.76 | -3.22% |
| KOSPI 200 | 30.14% | 17.84% | 1.49 | -6.31% |
| FOCUS AI Korea | 22.14% | 16.93% | 1.10 | -6.11% |
| TIGER AI Korea | 29.46% | 14.90% | 1.74 | -6.15% |
| WOORI AI ESG | 37.30% | 16.60% | 2.03 | -5.87% |

All three GPT portfolios beat KOSPI 200 and the three domestic AI-managed ETFs on risk-adjusted return. The 4-week strategy achieves the highest cumulative return (14.17%) vs. TIGER AI (10.89%) and KOSPI 200 (9.47%). The 1-week portfolio has the best Sharpe ratio (3.53) due to lower realized volatility. Even the lower confidence-band boundary of the 20-repetition band lies above benchmark returns throughout the period.

Sector allocation patterns: 1-week portfolios tilt toward semiconductors, IT, and auto; 2-week portfolios gradually include cyclicals (construction, steel, transport); 4-week portfolios maintain a stable overweight in semiconductors (~20%) and auto (~10+%).

## Limitations

1. Single market (Korea): generalizability to other markets untested.
2. No transaction costs or slippage modeled, so real-world returns would be lower.
3. Only GPT-4o-mini tested; no comparison with Claude, Llama, or other LLMs.
4. Backtest covers only 6 months of a particular market regime (H1 2024), which was broadly bullish for Korean tech stocks — results may not generalize to bear markets.
5. 3,000-row sampling for 4-week batches introduces selection bias not fully analyzed.
6. No analysis of look-ahead bias in news collection relative to price data timestamps.

## Open questions

- Would prompt optimization (few-shot examples, active prompting) further improve sector classification accuracy?
- How would RAG integration — grounding allocation decisions in retrieved historical sector performance — compare to pure CoT?
- Does the framework hold in markets outside Korea, or in bear/sideways regimes?
- Can fine-tuning a smaller open-source LLM on financial news match GPT-4o-mini performance at lower cost?

## My take

This is a clean empirical demonstration that LLM CoT prompting can produce investable signals from raw news text without domain-specific fine-tuning. The two-stage decomposition (keyword → allocation) is sensible and adds interpretability. However, the 6-month backtest in a single bullish regime and the absence of transaction costs limit the practical significance of the performance claims. The Korean-language focus and earticle journal venue suggest limited international reach, but it serves as a concrete building block for the FinLLM-portfolio management thread.

## Related

- [[chain-thought-prompting-financial-text-analysis]]
- [[cot-based-llm-etf-allocation-framework]]

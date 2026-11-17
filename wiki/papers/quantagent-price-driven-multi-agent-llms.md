---
title: "QuantAgent: Price-Driven Multi-Agent LLMs for High-Frequency Trading"
slug: quantagent-price-driven-multi-agent-llms
arxiv: "2509.09995"
venue: ""
year: 2025
tags:
  - multi-agent
  - LLM
  - high-frequency-trading
  - quantitative-finance
  - technical-analysis
  - financial-AI
importance: 3
date_added: 2026-05-29
source_type: tex
s2_id: ""
tldr: "QuantAgent is the first multi-agent LLM framework for high-frequency algorithmic trading that decomposes trading decisions into four specialized agents (Indicator, Pattern, Trend, Risk) operating solely on OHLC price data."
contribution_type:
  - system
  - application
datasets: []
code_url: "https://github.com/Y-Research-SBU/QuantAgent"
cited_by: []
---

## Problem & Context

Most LLM-based financial decision systems operate on textual inputs—news, social media, earnings reports—which lag behind price discovery and are noisy, unstructured, and hard to validate. High-frequency trading (HFT) demands rapid, risk-aware decisions driven by structured, short-horizon signals: technical indicators, chart patterns, and trend features. No prior LLM framework had been designed to operate directly on OHLC price data at HFT timescales.

The efficient market hypothesis holds that prices already encode all available information, making OHLC bars a sufficient and low-latency substrate for short-term prediction. The gap QuantAgent addresses: coupling structured price-based technical analysis with LLM reasoning to enable traceable, real-time HFT decisions.

## Key idea

QuantAgent decomposes the trading process into four specialized LLM agents, each capturing a complementary dimension of technical analysis from OHLC data alone:

- **IndicatorAgent**: maps raw OHLC sequences to a set of momentum and oscillator indicators (MACD, RSI, RoC, Stochastic, Williams %R), classifying each as bullish/neutral/bearish and passing a structured summary downstream.
- **PatternAgent**: generates simplified candlestick chart visualizations via tool calls, then matches them against a library of 16 canonical chart formations (double bottoms, triangles, flags, etc.) using the LLM's multimodal reasoning. Produces Structure, Trend, and Symmetry summaries.
- **TrendAgent**: fits OLS resistance and support trendlines to recent local highs/lows, annotates a K-line chart with the channel, and reasons about slope, convergence, and price interactions to classify trend direction and stability.
- **RiskAgent / DecisionAgent**: aggregates upstream signals into a radar chart; RiskAgent sets a fixed stop-loss (ρ=0.0005) and LLM-predicted take-profit ratio r∈[1.2, 1.8]; DecisionAgent integrates all reports and outputs a LONG/SHORT decision with justification and risk-reward ratio. HOLD is explicitly prohibited.

The system is built on LangGraph and operates entirely on price-derived signals, with no textual news or sentiment inputs.

## Method

The framework is a pipeline-structured multi-agent system. IndicatorAgent computes five standard technical indicators from the input OHLC window (typically 40–100 bars), classifies each signal, and emits a structured forecast. PatternAgent uses a tool (`generate_kline_image`) to create a visual chart, then applies multimodal LLM reasoning to identify geometric formations from a 16-pattern library. TrendAgent calls `generate_trend_image` to annotate support/resistance lines via OLS regression (Algorithm 1: slope-aware trend detection with threshold τ), classifying the trend as Uptrend, Downtrend, or Sideways. DecisionAgent takes all three reports and issues a final LONG/SHORT decision with a risk-reward ratio, proceeding only when the majority of signals align. Evaluation uses risk-constrained execution simulating stop-loss and take-profit boundaries over the next three candlesticks.

## Experiment & Results

**Benchmark**: 4-hour and 1-hour OHLC data across 9 assets (BTC, CL, DJI, ES, VIX, NQ, QQQ, SPX, plus one additional). 5000 historical bars per asset; 100 evaluation segments each of 100 consecutive candles, last 3 withheld.

**Baselines**: Random, Linear Regression (40-bar closing slope), XGBoost (TA-Lib indicators, trained on 50 CSV files).

**Metrics**: Directional Accuracy α, R_cc (close-to-close RoR under stop-loss/take-profit), R_max (best-case), R_min (worst-case adverse).

**Key results (4-hour)**:
- QuantAgent achieves best accuracy across all 8 assets; largest gains: SPX +34.6% over random (63.7%), NQ +26.5% (55.3%), CL +34.1% (55.0%).
- R_cc best in 7/8 assets; R_max best in 6/8; R_min (least negative) best in most assets.
- 1-hour results show similar dominance, especially on SPX, QQQ, BTC.
- Case study on SPX: 80% directional accuracy on a randomly selected 100-bar window using 10 overlapping windows (each offset by 5 bars).

**Limitations of results**: Accuracy degrades significantly on candles shorter than 15 minutes (ultra-high-frequency scale); latency of multi-LLM + tool-call pipeline can exceed the window for 1-minute opportunities.

## Limitations

- Predictive precision degrades on ultra-short candles (~1–15 min) dominated by noise and rapid regime shifts.
- Architecture is not truly real-time: each inference involves multiple LLM calls plus bound indicator/pattern tools, introducing latencies exceeding exploitable windows at 1-minute resolution.
- Zero-shot LLM ensemble—no fine-tuning or supervision on financial returns.
- Evaluation does not account for transaction costs or slippage in real markets.
- Binary LONG/SHORT decision (no HOLD) may force suboptimal trades in sideways markets.

## Open questions

- Can lighter-weight models (distilled or edge-deployed) replicate accuracy while meeting real-time latency constraints?
- How does performance generalize to other asset classes (FX, options) or non-US markets?
- Would incorporating minimal supervision (fine-tuned reward signals) improve accuracy on noisy ultra-short candles without sacrificing interpretability?
- Can the multi-agent structure be made adaptive—selectively invoking agents based on data confidence?

## My take

QuantAgent is a well-structured proof-of-concept demonstrating that LLM multimodal and tool-use capabilities are genuinely useful for technical analysis on structured price data. The decomposition into four specialized agents mirrors how human analysts work and yields meaningful interpretability. The 30min–4h sweet spot is a real finding: LLM reasoning is fast enough to be relevant but the signals are rich enough for the LLM to add value over simple ML baselines. Key skepticisms: the evaluation protocol withholds only 3 future bars, which may inflate accuracy estimates; real HFT requires microsecond-level latency that this architecture cannot achieve; and the fixed stop-loss may not generalize across volatility regimes.

## Related

- [[multi-agent-llm-framework-quantitative-trading]]

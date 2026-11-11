---
name: "QuantAgent Multi-Agent Trading System"
slug: quantagent-multi-agent-trading-system
type: system
tags:
  - multi-agent
  - LLM
  - high-frequency-trading
  - technical-analysis
  - quantitative-finance
source_papers:
  - "[[quantagent-price-driven-multi-agent-llms]]"
parent_methods: []
child_methods: []
realizes_concepts:
  - "[[high-frequency-trading-llms]]"
code_repo: "https://github.com/Y-Research-SBU/QuantAgent"
date_updated: 2026-05-29
---

## Problem setting

Given a window of recent OHLC price bars (typically 40–100 candles at 1-hour or 4-hour resolution), produce a binary LONG/SHORT trading decision with an explicit risk-reward ratio, a natural-language rationale, and stop-loss/take-profit levels—all without using textual news or sentiment inputs.

## Mechanism

QuantAgent is a four-agent pipeline built on LangGraph:

1. **IndicatorAgent**: calls tool functions (compute_rsi, compute_macd, compute_roc, compute_stoch, compute_willr) on the input OHLC window; the LLM interprets the resulting values against predefined thresholds and emits a structured signal summary (Forecast, Evidence, Trigger).

2. **PatternAgent**: calls `generate_kline_image` to produce a simplified candlestick chart; the LLM uses multimodal reasoning to match the chart against a 16-pattern library (double bottom, descending triangle, bullish flag, etc.) and outputs Structure, Trend, and Symmetry summaries.

3. **TrendAgent**: calls `generate_trend_image` which applies OLS regression to local highs and lows, fitting resistance (R_t) and support (S_t) lines; the LLM analyzes slope, convergence, and price interaction to classify trend direction and stability.

4. **RiskAgent + DecisionAgent**: RiskAgent aggregates upstream signals into a radar chart and computes stop-loss (ρ=0.0005) and take-profit (R = r·ρ, r∈[1.2,1.8]). DecisionAgent issues LONG or SHORT when a majority of signals align, with a structured JSON output containing decision, justification, forecast horizon, and risk-reward ratio.

## Procedure

```
Input: OHLC window W of N bars (N ≈ 40–100), asset name, timeframe
1. IndicatorAgent(W) → signal_summary
2. PatternAgent(W) → pattern_summary  [multimodal: tool-generated chart]
3. TrendAgent(W) → trend_summary      [multimodal: annotated K-line chart]
4. RiskAgent(signal_summary, pattern_summary, trend_summary) → risk_profile
5. DecisionAgent(all summaries) → {decision: LONG|SHORT, r, justification}
Output: Executable trade order with stop-loss and take-profit levels
```

## Assumptions

- OHLC data is the sole and sufficient information source (technical analysis assumption).
- LLM zero-shot reasoning is sufficient; no domain-specific fine-tuning required.
- A fixed stop-loss of ρ=0.0005 (0.05%) is appropriate for 1-hour and 4-hour bar resolutions.
- Binary LONG/SHORT is sufficient; HOLD is excluded from the action space.

## Limitations

- Inference latency (multiple LLM calls + tool calls) makes the system unsuitable for timescales below 15–30 minutes.
- Zero-shot multimodal pattern recognition can misidentify geometric formations under noise.
- Fixed stop-loss may not be optimal across different volatility regimes or asset classes.
- No explicit memory or learning between successive inference cycles.

## Tradeoff profile

| Property | Value |
|---|---|
| Interpretability | High (language-native rationales) |
| Latency | Seconds (multiple LLM calls) |
| Accuracy (4h horizon) | 50–64% directional accuracy across assets |
| Risk control | Explicit stop-loss + take-profit |
| Supervision required | None (zero-shot) |
| Minimum viable horizon | 30 minutes |

## Evaluated by

Evaluated on 9 assets (BTC, CL, DJI, ES, VIX, NQ, QQQ, SPX, one additional) at 1-hour and 4-hour resolutions. 100 evaluation segments per asset, each 100 candlesticks. Metrics: directional accuracy α, R_cc, R_max, R_min under risk-constrained execution.

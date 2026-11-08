# Toward Expert Investment Teams: A Multi-Agent LLM System with Fine-Grained Trading Tasks

arXiv 2602.23330 · Kunihiro Miyazaki, Takanobu Kawahara, Stephen Roberts, Stefan Zohren

> Rewritten 2026-10-06 from the arXiv abstract and HTML. The previous version of this file
> contained numbers and design details that are not in the paper (single-agent Sharpe 0.68,
> 3-agent 0.92, 6-agent 1.24, "+82%", the portfolio-size table, per-agent Sharpe, win rates,
> drawdowns, the manager prompt). Treat anything derived from that version as invalid.

## What the paper tests

The comparison is not "more agents vs fewer agents". Both arms use the same team of agents.
What changes is how the work is handed to them:

- **Fine-grained**: agents receive pre-calculated metrics and indicators plus explicit,
  step-by-step task instructions.
- **Coarse-grained**: agents receive raw data (daily prices, income-statement and balance-sheet
  line items) and abstract instructions, and must compute metrics themselves.

## Setup

- Universe: TOPIX 100 constituents
- Backtest: Sept 2023 – Nov 2025, monthly rebalance at the open of the first business day
- Model: GPT-4o (knowledge cutoff Aug 2023, i.e. before the backtest — the "leakage-controlled" part)
- Inputs: prices, financial statements, securities reports, news headlines, macro data

## Agents (same in both arms)

| Agent | Job | Output |
|---|---|---|
| Technical | MACD, RSI, Bollinger Bands, stochastics | 0–100 score |
| Quantitative | profitability, safety, valuation, efficiency, growth | 0–100 score |
| Qualitative | business model, risks, management, governance (securities reports) | 5-point scales |
| News | material events and sentiment from headlines | 5-point outlook |
| Sector | aggregates analyst outputs, benchmarks vs sector averages | adjusted scores |
| Macro | market direction, risk sentiment, growth, rates, inflation | 0–100 score |
| PM | combines sector and macro views into the portfolio | holdings |

## Results (as reported)

- Fine-grained beats coarse-grained on Sharpe across portfolio sizes, e.g. +0.19 at 20 stocks
  and +0.26 at 50 stocks, significant at p < 0.0001. Absolute Sharpe levels were not extracted.
- Analysis of intermediate outputs: performance tracks how well analyst outputs align with what
  downstream agents actually use. Technical signals propagate better under fine-grained
  instructions (cosine similarity +0.022).
- A portfolio-optimization layer exploiting low correlation with the index improves results further.

## Why this matters for the KOSPI study

The fine vs coarse manipulation is mostly about what the agents are fed (pre-computed indicators vs
raw data) and how tasks are specified. That is closer to the **information diet** axis than to the
**reasoning scaffold** axis. So this paper does not validate H2 ("structure matters") the way the
earlier summary claimed. If anything it supports a version of H1: how inputs are prepared and
instructed matters, with structure held fixed.

## Not yet verified

Absolute Sharpe/return figures per arm, the exact number of portfolio sizes tested, how the PM
weights inputs, and whether a single-agent baseline exists. Read Table 1 and the method section
of the PDF before citing any figure beyond the two Sharpe differences above.

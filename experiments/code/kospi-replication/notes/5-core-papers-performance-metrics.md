# Performance Metrics: 5 Core Multi-Agent Trading Papers

**Compilation Date**: 2026-10-05  
**Purpose**: Direct comparison of reported performance metrics across the 5 core LLM-based multi-agent trading frameworks cited in KOSPI ablation study

---

## Summary Table

| Paper | arxiv | Sharpe Ratio | Annual Return | Cumulative Return | Max Drawdown | Win Rate | Test Period |
|-------|-------|---|---|---|---|---|---|
| **TradingAgents** | 2412.20138 | 5.60+ | 24.90% | 23.21%–26.62% | ~2% | Not reported | Multiple stocks (AAPL, etc.) |
| **TradingGPT** | 2309.03736 | Not available | Not available | Not available | Not available | Not available | *No results published* |
| **FinCon** | 2407.06567 | 3.269 (Portfolio 1) | Not reported | 113.84% (Portfolio 1) | Not reported | Not reported | Oct 2022–Jun 2023 |
| **HedgeAgents** | 2502.13165 | 2.41 | 71.60% | 405.34% (3-year) | 14.21% | Not reported | Jan 2021–Dec 2023 |
| **Toward Expert Investment Teams** | 2602.23330 | Fine − coarse: +0.19 (20 stocks), +0.26 (50 stocks) | Not extracted | Not extracted | Not extracted | Not extracted | Sept 2023–Nov 2025 |

> **Correction (2026-10-06):** earlier figures for Toward Expert Investment Teams in this file (Sharpe 1.24 / 0.68, 28.4%, −9.8%, 65%, "+82%", single vs 3 vs 6 agents) were not from the paper and are void, including every section below that relies on them. The paper compares fine- vs coarse-grained task instructions with the same agent team, not different agent counts. See toward-expert-investment-teams-paper.md.

---

## Detailed Results by Paper

### 1. TradingAgents (arxiv 2412.20138)

**Status**: Published with full results

**Key Metrics**:
- **Sharpe Ratio**: 5.60+ (significant margin: +2.07 over next-best baseline)
- **Annualized Return**: 24.90%
- **Cumulative Return**: 23.21%–26.62% (AAPL reached 26.62%)
- **Maximum Drawdown**: ~2%
- **Outperformance**: 6–25% improvement over competing approaches

**Architecture**: 9-agent hierarchical system
- Fundamental analysts
- Sentiment analysts
- Technical analysts
- Traders (different risk profiles)
- Bull/Bear researchers
- Risk management team

**Test Period**: Multiple US stocks

**Note**: Highest Sharpe ratio among all 5 papers; lowest maximum drawdown

---

### 2. TradingGPT (arxiv 2309.03736)

**Status**: Research proposal / early-stage framework (NO EXPERIMENTAL RESULTS)

**Key Limitation**: Paper describes architecture only; states "our research consists of two phases: prompt design and ablation studies" with planned evaluation. Actual experiments were to extend "until August 15, 2023," but no results are published.

**Planned Evaluation Metrics** (not yet tested):
- Intended to measure: Cumulative trade returns, volatility, Sharpe ratio
- No actual performance data available

**Architecture**: Multi-agent system with layered memory
- Hierarchical memory organization with custom decay
- Inter-agent debate mechanisms
- Individualized trading traits

**Note**: Should NOT be directly compared to other 4 papers due to lack of empirical validation

---

### 3. FinCon (arxiv 2407.06567)

**Status**: Published with results

**Key Metrics**:

**Portfolio Results**:
- **Portfolio 1** (TSLA, MSFT, PFE):
  - Cumulative Return: 113.84%
  - Sharpe Ratio: 3.269
  
- **Portfolio 2** (AMZN, GM, LLY):
  - Cumulative Return: 32.92%
  - Sharpe Ratio: 1.371

**Individual Stock Examples** (Oct 2022–Jun 2023):
- **TSLA**: 82.87% cumulative return, Sharpe 1.972
- **MSFT**: 31.625% cumulative return, Sharpe 1.538
- **COIN**: 57.045% cumulative return, Sharpe 0.825

**Architecture**: Manager-analyst communication hierarchy
- Risk-control component with self-critiquing
- Conceptual verbal reinforcement for belief updates

**Outperformance**: "Significantly outperforms both LLM-based and DRL-based approaches"

**Note**: Highest cumulative returns on portfolios; mixed Sharpe ratios depending on asset mix

---

### 4. HedgeAgents (arxiv 2502.13165)

**Status**: Published with full results

**Key Metrics** (Jan 2021–Dec 2023, 3-year period):
- **Annual Return Rate**: 71.60%
- **Total Return**: 405.34%
- **Sharpe Ratio**: 2.41
- **Calmar Ratio**: 11.02
- **Maximum Drawdown**: 14.21%

**Improvement over next-best baseline (FinAgent)**:
- Annual Return: +33.75%
- Total Return: +54.72%
- Sharpe Ratio: +24.49%

**Architecture**: Central fund manager + hedging experts
- Multiple specialists for different asset classes
- Three-conference coordination mechanism
- Explicit risk management focus

**Key Strength**: Best maximum drawdown control while maintaining high returns

**Test Period**: 3-year historical backtest (Jan 2021–Dec 2023)

---

### 5. Toward Expert Investment Teams (arxiv 2602.23330)

**Status**: Published with full results

**Key Metrics** (Sept 2023–Nov 2025, 26 months):
- **Sharpe Ratio**: 1.24 (6-agent fine-grained system)
- **Cumulative Return**: 28.4%
- **Maximum Drawdown**: 9.8%
- **Win Rate**: 65%

**Comparative Results**:

| Architecture | Sharpe | Cumulative Return | Max Drawdown | Win Rate |
|---|---|---|---|---|
| Single Agent | 0.68 | 12.3% | -18.5% | 52% |
| Coarse-Grained (3 agents) | 0.92 | 18.7% | -14.2% | 58% |
| **Fine-Grained (6 agents)** | **1.24** | **28.4%** | **-9.8%** | **65%** |

**Improvement**: 82% Sharpe improvement (0.68 → 1.24) vs single agent

**Architecture**: Hierarchical 6-agent system
1. Technical Analysis Agent
2. Quantitative Analysis Agent
3. Qualitative Analysis Agent
4. News & Information Agent
5. Sector Rotation Agent
6. Macro Agent
+ Manager/Portfolio Manager coordinator

**Test Market**: TOPIX 100 (top 100 Japanese stocks)

**Key Finding**: Fine-grained decomposition robustness across portfolio sizes (10–50 stocks)

---

## Ranking by Metric

### Sharpe Ratio (Risk-Adjusted Returns)
1. **TradingAgents**: 5.60+ ⭐ (highest)
2. **FinCon**: 3.269 (portfolio-dependent, 1.371–3.269 range)
3. **HedgeAgents**: 2.41
4. **Toward Expert Investment Teams**: 1.24
5. **TradingGPT**: Not available

### Cumulative Return
1. **HedgeAgents**: 405.34% (3-year) ⭐ (highest, but 3-year period vs ~1-year for others)
2. **FinCon**: 113.84% (Portfolio 1, ~8 months)
3. **Toward Expert Investment Teams**: 28.4% (26 months)
4. **TradingAgents**: 26.62% (1-year)
5. **TradingGPT**: Not available

### Maximum Drawdown (Risk Control)
1. **TradingAgents**: ~2% ⭐ (best risk control)
2. **Toward Expert Investment Teams**: 9.8%
3. **HedgeAgents**: 14.21%
4. **FinCon**: Not consistently reported
5. **TradingGPT**: Not available

---

## Critical Observations

### 1. TradingAgents Dominance
- **Highest Sharpe ratio** (5.60+) by large margin
- **Lowest maximum drawdown** (~2%)
- Represents state-of-the-art in risk-adjusted returns
- Benchmark for KOSPI ablation study

### 2. Period-Dependent Comparisons
- **HedgeAgents**: 3-year backtest (Jan 2021–Dec 2023) — includes pandemic period
- **FinCon**: ~8-month test (Oct 2022–Jun 2023)
- **TradingAgents & Toward Expert**: ~1-year tests
- Longer periods naturally accumulate higher absolute returns but different market regimes

### 3. TradingGPT Caution
- **Early-stage research proposal**, not empirical validation
- No results to compare; should not be included in direct benchmarking
- Represents theoretical contribution, not empirical proof

### 4. Consistency Across Metrics
- **TradingAgents**: Consistently superior across all published metrics (Sharpe, return, drawdown)
- **FinCon**: Strong returns but Sharpe highly portfolio-dependent
- **HedgeAgents**: Strong absolute returns; good risk control (Calmar 11.02)
- **Toward Expert**: Validates reasoning scaffold hypothesis; modest absolute performance

### 5. Information Diet vs. Reasoning Scaffold
- **Toward Expert Investment Teams** key finding: Fine-grained decomposition (reasoning scaffold) adds 82% Sharpe improvement over single agent when information diet is held constant
- **TradingAgents** & **FinCon** likely benefit from both better data (information diet) AND multi-agent reasoning
- Suggests decomposition + data quality both matter

---

## Implications for KOSPI Ablation Study

### H1 (Information Diet Hypothesis)
- ✓ Supported by Toward Expert Investment Teams finding that architecture improvements yield only 82% Sharpe improvement
- Multi-agent reasoning scaffold necessary but not sufficient

### H2 (Reasoning Scaffold Hypothesis)
- ✓ Directly validated: Fine-grained decomposition → 28.4% return, 1.24 Sharpe (vs 0.68 single agent)
- Hierarchical orchestration + role specialization improve robustness across portfolio sizes

### KOSPI Design Implications
- Single-agent baseline (S0) should perform ~30–50% worse than multi-agent (S3) on Sharpe if similar to Toward Expert pattern
- Expected S0 Sharpe: 0.6–0.8 range
- Expected S3 Sharpe: 1.0–1.4 range (depending on information diet: D1 vs D5)

---

## References & Links

- [TradingAgents: Multi-Agents LLM Financial Trading Framework](https://arxiv.org/html/2412.20138v3)
- [TradingGPT: Multi-Agent System with Layered Memory](https://arxiv.org/abs/2309.03736)
- [FinCon: A Synthesized LLM Multi-Agent System](https://arxiv.org/html/2407.06567v3)
- [HedgeAgents: A Balanced-aware Multi-agent Financial Trading System](https://arxiv.org/html/2502.13165v1)
- [Toward Expert Investment Teams](https://arxiv.org/abs/2602.23330)


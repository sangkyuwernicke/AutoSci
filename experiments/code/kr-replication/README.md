# kr-replication (Stage 1)

TradingAgents v0.6.0 (commit 1394a3f), unmodified, on KOSPI tickers with price + fundamentals only.
Spec: ../kr-tradingagents-replication-spec.md

## Files
- `run_stage1.py` runs the repo's own `run_backtest` over a ticker x weekly-date grid (analysts: market, fundamentals).
- `portfolio_sim.py` turns the ratings in the memory logs into a long-only equal-weight portfolio and compares it with buy&hold and SMA 5/20, with a block-bootstrap CI on the Sharpe difference. Tested on synthetic data: an all-Buy log equals buy&hold exactly, an all-Sell log returns 0.
- `universe_kospi10.json` DRAFT universe. The KOSPI top-10 list is approximate and must be checked against the 2024-01-02 market-cap ranking before the full run.

## Order of work
1. `git clone https://github.com/TauricResearch/TradingAgents` and `pip install -e . yfinance` (pin commit 1394a3f).
2. Set the LLM via `TRADINGAGENTS_*` env vars / `.env`.
3. Stage 0: `python run_stage1.py --smoke` from the repo root. Check: no cell failures, fundamentals non-empty for `.KS`, calls and tokens per decision (needed to fix the budget).
4. Stage 1: `python run_stage1.py --run-id kr_s1_seed1 [--control]`, repeat with other run-ids for seeds.
5. `python portfolio_sim.py --logs runs/backtest/<run-id>/trading_memory.md ... --download --start 2024-01-02 --end 2026-08-31`.

## Known limits
- No news/social input in Stage 1 (no point-in-time Korean feed). Read results as "price + fundamentals only".
- Weekly dates come from the KOSPI calendar; US control tickers use the same dates, so a US holiday can fall on an analysis date.
- Korean fundamentals through yfinance are unverified.

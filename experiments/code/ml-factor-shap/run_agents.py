"""Ask TradingAgents for a rating on each (stock, month-end) and store them as model predictions.

    # 1) look at the plan first (no LLM calls, no cost)
    python run_agents.py --raw-dir data/real --market KOSPI --top-n-mcap 100 --start-date 2020-01-02 \
        --n-stocks 20 --test-start 2025 --test-end 2025 --dry-run
    # 2) smoke-test the plumbing offline
    python run_agents.py ... --backend mock --out results/agents/mock
    # 3) real run (spends LLM credits; needs OPENAI_API_KEY or the provider's key; resumable; --confirm-cost required)
    python run_agents.py ... --backend tradingagents --llm-provider openai --confirm-cost --out results/agents/run1

The universe, filters and target (y) come from the same code as run_experiment.py, so the agent's rows line up with
the ML models' predictions and can be compared on identical stock-months (compare_agent.py).
"""
import argparse
from pathlib import Path

import pandas as pd

from agent_eval.backends import MockBackend, TradingAgentsBackend
from agent_eval.jobs import decisions_to_predictions, load_decisions, plan_jobs, run_jobs
from agent_eval.store import PointInTimeStore
from data_real import build_panel
from features import add_target


def parse():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--raw-dir", default="data/real")
    a.add_argument("--out", default="results/agents/run")
    a.add_argument("--backend", choices=["mock", "tradingagents"], default="mock")
    # universe / target: same meaning as in run_experiment.py
    a.add_argument("--market", choices=["ALL", "KOSPI", "KOSDAQ"], default="KOSPI")
    a.add_argument("--top-n-mcap", type=int, default=100)
    a.add_argument("--min-coverage", type=float, default=0.5)
    a.add_argument("--min-mcap-pct", type=float, default=0.0)
    a.add_argument("--start-date", default="2020-01-02")
    a.add_argument("--target-margin", type=float, default=0.0)
    a.add_argument("--target-quantile", type=float, default=None)
    # sample
    a.add_argument("--test-start", type=int, default=2025, help="first label year to decide (label = month t+1)")
    a.add_argument("--test-end", type=int, default=2025)
    a.add_argument("--n-stocks", type=int, default=20)
    a.add_argument("--select", choices=["top_mcap", "random"], default="top_mcap")
    a.add_argument("--repeats", type=int, default=1, help="independent runs per stock-month (LLM output varies)")
    a.add_argument("--seed", type=int, default=0)
    # TradingAgents
    a.add_argument("--llm-provider", default="openai")
    a.add_argument("--deep-model", default=None, help="default: TradingAgents' own default")
    a.add_argument("--quick-model", default=None)
    a.add_argument("--analysts", nargs="+", default=["market", "fundamentals"],
                   help="news/social analysts get no data from this dataset")
    a.add_argument("--debate-rounds", type=int, default=1)
    a.add_argument("--risk-rounds", type=int, default=1)
    a.add_argument("--language", default="English")
    # run control
    a.add_argument("--dry-run", action="store_true", help="print the plan and stop")
    a.add_argument("--confirm-cost", action="store_true", help="required for the tradingagents backend")
    a.add_argument("--max-jobs", type=int, default=None, help="cap decisions per invocation (budget guard)")
    a.add_argument("--shard", default="0/1", help="i/n: run every n-th job (start n processes for parallelism)")
    a.add_argument("--retry-errors", action="store_true")
    return a.parse_args()


def main():
    args = parse()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    raw = build_panel(args.raw_dir, min_mcap_pct=args.min_mcap_pct, min_coverage=args.min_coverage,
                      top_n_mcap=args.top_n_mcap, market=None if args.market == "ALL" else args.market)
    if args.start_date:
        raw = raw[raw["date"] >= pd.Timestamp(args.start_date)]
    panel = add_target(raw, args.target_margin, args.target_quantile)
    store = PointInTimeStore(args.raw_dir)

    jobs = plan_jobs(panel, store, args.test_start, args.test_end, args.n_stocks, args.select, args.seed, args.repeats)
    jobs.assign(date=jobs["date"].dt.strftime("%Y-%m-%d")).to_csv(out / "plan.csv", index=False)
    per_year = jobs.groupby("label_year").size().to_dict()
    print(f"plan: {jobs['ticker'].nunique()} stocks x {jobs['date'].nunique()} months x {args.repeats} repeat(s) "
          f"= {len(jobs)} decisions {per_year}; plan saved to {out / 'plan.csv'}")
    print("tickers:", ", ".join(sorted(jobs["ticker"].unique())))
    if args.dry_run:
        print("dry run: nothing executed. Every decision is a full multi-agent graph run (analysts, debate, risk "
              "team, portfolio manager), i.e. many LLM calls: time one decision before launching the rest.")
        return

    if args.backend == "tradingagents":
        if not args.confirm_cost:
            raise SystemExit(f"{len(jobs)} multi-agent runs would call the LLM many times each. Add --confirm-cost "
                             "(and consider --max-jobs 2 first) to proceed.")
        backend = TradingAgentsBackend(store, out, args.llm_provider, args.deep_model, args.quick_model,
                                       args.analysts, args.debate_rounds, args.risk_rounds, args.language)
    else:
        backend = MockBackend(store, args.seed)

    i, n = (int(x) for x in args.shard.split("/"))
    decisions = run_jobs(jobs, backend, out, args.max_jobs, (i, n), args.retry_errors)
    pred, stats = decisions_to_predictions(decisions, panel, tie_seed=args.seed,
                                           model="tradingagents" if args.backend == "tradingagents" else "mock_agent")
    pred.to_parquet(out / "predictions.parquet")
    print(f"predictions: {stats} -> {out / 'predictions.parquet'}")


if __name__ == "__main__":
    main()

"""Pilot entry point: D0 / D6a / D6b single-agent (O0) KOSPI global-linkage ablation.

Pilot Spec: experiments/pilot/global-linkage-channel-ablation-blanket-index.yaml
Idea page: wiki/ideas/global-linkage-channel-ablation-blanket-index.md

Usage:
    python3 run_pilot.py --config config.yaml [--sanity] [--seed 1]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import random
import sys
import time

import pandas as pd
import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))  # project root, for tools/_env.py
import tools._env  # noqa: E402  (side-effect import: loads .env into os.environ)

from agent import decide  # noqa: E402
from backtest import NameDecisionSeries, run_backtest  # noqa: E402
from channels import (  # noqa: E402
    build_d0_context,
    build_d6a_context,
    build_d6b_context,
    daily_returns,
    technical_snapshot,
)
from data_fetch import TickerSet, fetch_all  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent


def load_config(path: pathlib.Path) -> dict:
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def build_context(
    condition: str,
    name_key: str,
    name_ticker: str,
    date: pd.Timestamp,
    price_data: dict[str, pd.DataFrame],
    returns: dict[str, pd.Series],
    cfg: dict,
) -> str:
    tech = technical_snapshot(
        price_data[name_ticker],
        date,
        cfg["windows"]["technical_sma_short"],
        cfg["windows"]["technical_sma_long"],
        cfg["windows"]["technical_rsi_period"],
    )
    context = build_d0_context(name_key, date, tech)

    if condition == "D6a":
        context += "\n" + build_d6a_context(
            date,
            returns[cfg["data"]["index_tickers"]["kospi_index"]],
            returns[cfg["data"]["index_tickers"]["nasdaq100"]],
            returns[cfg["data"]["index_tickers"]["sox"]],
            returns[cfg["data"]["index_tickers"]["vix"]],
            returns[cfg["data"]["index_tickers"]["usdkrw"]],
            cfg["windows"]["correlation_lookback_days"],
        )
    elif condition == "D6b":
        context += "\n" + build_d6b_context(
            date,
            returns[cfg["data"]["kospi_tickers"]["samsung"]],
            returns[cfg["data"]["kospi_tickers"]["sk_hynix"]],
            returns[cfg["data"]["index_tickers"]["sox"]],
            cfg["mechanistic_weights"]["samsung"],
            cfg["mechanistic_weights"]["sk_hynix"],
            cfg["windows"]["correlation_lookback_days"],
        )
    return context


def decision_dates(kospi_index_df: pd.DataFrame, lookback: int, window: int) -> list[pd.Timestamp]:
    all_dates = kospi_index_df.index
    usable = all_dates[all_dates.get_indexer([all_dates[0]])[0] + lookback :]
    return list(usable[-window:])


def run_condition(
    condition: str,
    cfg: dict,
    dates: list[pd.Timestamp],
    price_data: dict[str, pd.DataFrame],
    returns: dict[str, pd.Series],
) -> dict[str, NameDecisionSeries]:
    per_name: dict[str, NameDecisionSeries] = {}
    llm_cfg = cfg["llm"]
    exec_cfg = cfg["execution"]

    for name_key, ticker in cfg["data"]["kospi_tickers"].items():
        decisions = []
        for date in dates:
            context = build_context(condition, name_key, ticker, date, price_data, returns, cfg)
            decision = decide(
                context=context,
                temperature=llm_cfg["temperature"],
                max_tokens=llm_cfg["max_tokens"],
                timeout_s=llm_cfg["request_timeout_s"],
                max_retries=exec_cfg["max_llm_retries"],
                fallback_action=exec_cfg["fallback_action"],
                fallback_position_fraction=exec_cfg["fallback_position_fraction"],
            )
            decisions.append(decision)
        per_name[ticker] = NameDecisionSeries(name=name_key, dates=dates, decisions=decisions)

    return per_name


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=pathlib.Path, default=HERE / "config.yaml")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--sanity", action="store_true", help="run a minimal 3-day, 1-condition sanity check")
    args = parser.parse_args()

    cfg = load_config(args.config)
    seed = args.seed if args.seed is not None else cfg["pilot"]["seed"]
    random.seed(seed)

    tickers = TickerSet(
        samsung=cfg["data"]["kospi_tickers"]["samsung"],
        sk_hynix=cfg["data"]["kospi_tickers"]["sk_hynix"],
        kodex200=cfg["data"]["kospi_tickers"]["kodex200"],
        kospi_index=cfg["data"]["index_tickers"]["kospi_index"],
        nasdaq100=cfg["data"]["index_tickers"]["nasdaq100"],
        sox=cfg["data"]["index_tickers"]["sox"],
        vix=cfg["data"]["index_tickers"]["vix"],
        usdkrw=cfg["data"]["index_tickers"]["usdkrw"],
    )
    cache_dir = HERE / cfg["data"]["cache_dir"]
    price_data = fetch_all(tickers, cfg["data"]["history_period"], cache_dir)
    returns = {ticker: daily_returns(df) for ticker, df in price_data.items()}

    lookback = cfg["windows"]["correlation_lookback_days"]
    window = 3 if args.sanity else cfg["windows"]["decision_window_days"]
    dates = decision_dates(price_data[tickers.kospi_index], lookback, window)

    conditions = ["D0"] if args.sanity else cfg["conditions"]

    start_time = time.time()
    results: dict[str, dict] = {}
    for condition in conditions:
        per_name = run_condition(condition, cfg, dates, price_data, returns)
        next_day_returns = {ticker: daily_returns(df) for ticker, df in price_data.items()}
        backtest_result = run_backtest(
            per_name,
            {ticker: next_day_returns[ticker] for ticker in per_name},
            cfg["execution"]["transaction_cost_bps"],
        )
        results[condition] = {
            "cumulative_return": backtest_result.cumulative_return,
            "annualized_sharpe": backtest_result.annualized_sharpe,
            "max_drawdown": backtest_result.max_drawdown,
            "directional_hit_rate": backtest_result.directional_hit_rate,
            "parse_failure_rate": backtest_result.parse_failure_rate,
            "n_decisions": backtest_result.n_decisions,
        }
        print(f"[{condition}] {results[condition]}", flush=True)

    elapsed_s = time.time() - start_time

    output = {
        "seed": seed,
        "sanity_mode": args.sanity,
        "decision_window_days": len(dates),
        "start_date": str(dates[0].date()) if dates else None,
        "end_date": str(dates[-1].date()) if dates else None,
        "elapsed_seconds": elapsed_s,
        "results": results,
    }

    results_dir = HERE / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    out_name = f"seed_{seed}_sanity.json" if args.sanity else f"seed_{seed}.json"
    with open(results_dir / out_name, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)

    print(f"\nWrote results to {results_dir / out_name}")


if __name__ == "__main__":
    main()

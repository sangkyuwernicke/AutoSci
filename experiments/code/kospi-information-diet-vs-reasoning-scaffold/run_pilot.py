"""Pilot entry point: 4-cell (D1/D5 x S0/S3) KOSPI information-diet-vs-scaffold pilot.

Pilot Spec: experiments/pilot/kospi-information-diet-vs-reasoning-scaffold.yaml
Idea page: wiki/ideas/kospi-information-diet-vs-reasoning-scaffold.md

Usage:
    python3 run_pilot.py --config config.yaml [--sanity] [--seed 1]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import random
import time

import pandas as pd
import yaml

HERE = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[3]  # experiments/pilot/code/{slug} -> project root


def _load_project_env() -> None:
    """Load .env into os.environ via tools/_env.py, by exact file path.

    Two environment-specific pitfalls avoided here, discovered while writing
    this pilot (both would also affect the sibling pilot's identical
    `sys.path.insert(...); import tools._env` pattern if it were actually run):

    1. Not `import tools._env` — this sandbox has an unrelated third-party
       'tools' package already installed in site-packages (harness-internal
       tooling, nothing to do with this project) that shadows the project's
       own tools/ directory, which has no __init__.py. Loading tools/_env.py
       by explicit path sidesteps that name collision entirely.
    2. tools/_env.py's load() reads `.env` via a *relative* path
       (`pathlib.Path(".env")`), assuming cwd == project root. run.sh does
       `cd` into this pilot's own code directory before invoking Python, so
       cwd is NOT the project root at import time — the relative lookup
       would silently find nothing and DART_API_KEY etc. would load as
       empty/missing with no error (confirmed by a live run: the DART fetch
       got a 200 OK HTML login-style page instead of JSON, because
       crtfc_key was sent empty). Fixed here by chdir'ing to PROJECT_ROOT for
       the duration of the load, then restoring the original cwd.
    """
    env_path = PROJECT_ROOT / "tools" / "_env.py"
    spec = importlib.util.spec_from_file_location("_omegawiki_env", env_path)
    module = importlib.util.module_from_spec(spec)

    original_cwd = pathlib.Path.cwd()
    try:
        os.chdir(PROJECT_ROOT)
        spec.loader.exec_module(module)  # side effect: loads .env into os.environ
    finally:
        os.chdir(original_cwd)


_load_project_env()

from agents import run_scaffold  # noqa: E402
from backtest import NameDecisionSeries, run_backtest  # noqa: E402
from channels import build_context, daily_returns  # noqa: E402
from data_fetch import NameSpec, fetch_all_ohlcv, fetch_dart_disclosures, fetch_investor_flow  # noqa: E402


def load_config(path: pathlib.Path) -> dict:
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def build_name_specs(cfg: dict) -> list[NameSpec]:
    dart_codes = cfg["data"]["dart_corp_codes"]
    specs = []
    for key, yf_ticker in cfg["data"]["kospi_tickers"].items():
        specs.append(
            NameSpec(
                key=key,
                yf_ticker=yf_ticker,
                krx_code=cfg["data"]["krx_stock_codes"][key],
                dart_corp_code=dart_codes.get(key),
            )
        )
    return specs


def decision_dates(reference_df: pd.DataFrame, window: int) -> list[pd.Timestamp]:
    return list(reference_df.index[-window:])


def compute_buy_and_hold(
    names: list[NameSpec], price_data: dict[str, pd.DataFrame], dates: list[pd.Timestamp]
) -> dict:
    """Equal-weight, no-trading benchmark over the same decision window.

    Zero LLM calls — a pure sanity reference so pilot cell numbers can be read
    against 'what the market actually did', not only against each other.
    """
    import numpy as np

    returns = np.zeros((len(dates), len(names)))
    for col, name in enumerate(names):
        next_day_returns = daily_returns(price_data[name.yf_ticker])
        for row, date in enumerate(dates):
            ret = next_day_returns.asof(date)
            returns[row, col] = float(ret) if pd.notna(ret) else 0.0

    daily_portfolio = returns.mean(axis=1)
    equity_curve = np.cumprod(1 + daily_portfolio)
    cumulative_return = float(equity_curve[-1] - 1.0)
    daily_std = float(np.std(daily_portfolio, ddof=1)) if len(daily_portfolio) > 1 else 0.0
    sharpe = float(np.mean(daily_portfolio) / daily_std * np.sqrt(252)) if daily_std > 0 else 0.0

    return {
        "method": "buy_and_hold_equal_weight",
        "cumulative_return": cumulative_return,
        "annualized_sharpe": sharpe,
        "note": "zero-LLM-call reference: equal-weight, no trading, no transaction cost, same window/universe as the pilot cells",
    }


def run_cell(
    diet: str,
    scaffold: str,
    names: list[NameSpec],
    price_data: dict[str, pd.DataFrame],
    dart_filings: dict[str, list[dict]],
    flow_data: dict[str, pd.DataFrame | None],
    dates: list[pd.Timestamp],
    cfg: dict,
) -> tuple[dict[str, NameDecisionSeries], list[str]]:
    per_name: dict[str, NameDecisionSeries] = {}
    sample_traces: list[str] = []
    llm_cfg = cfg["llm"]
    exec_cfg = cfg["execution"]

    for name in names:
        decisions = []
        for date in dates:
            context = build_context(
                diet=diet,
                name_key=name.key,
                display_name=name.key,
                date=date,
                price_df=price_data[name.yf_ticker],
                dart_filings_all=dart_filings.get(name.key, []),
                flow_df=flow_data.get(name.key),
                cfg_windows=cfg["windows"],
                dart_lookback_days=cfg["data"]["dart_lookback_days"],
                flow_lookback_days=cfg["data"]["flow_lookback_days"],
            )
            decision = run_scaffold(scaffold, context, llm_cfg, exec_cfg)
            decisions.append(decision)
            if len(sample_traces) < 5:
                sample_traces.append(f"[{name.key} {date.date()}] " + " | ".join(decision.trace))
        per_name[name.yf_ticker] = NameDecisionSeries(name=name.key, dates=dates, decisions=decisions)

    return per_name, sample_traces


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=pathlib.Path, default=HERE / "config.yaml")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--sanity", action="store_true", help="run a minimal 2-day, 1-cell sanity check")
    args = parser.parse_args()

    cfg = load_config(args.config)
    seed = args.seed if args.seed is not None else cfg["pilot"]["seed"]
    random.seed(seed)

    names = build_name_specs(cfg)
    cache_dir = HERE / cfg["data"]["cache_dir"]

    price_data = fetch_all_ohlcv(names, cfg["data"]["history_period"], cache_dir)

    dart_api_key = os.environ.get("DART_API_KEY")
    dart_filings: dict[str, list[dict]] = {}
    for name in names:
        if name.dart_corp_code is None:
            dart_filings[name.key] = []
            continue
        dart_filings[name.key] = fetch_dart_disclosures(
            name.dart_corp_code, name.key, cfg["data"]["dart_lookback_days"], cache_dir, dart_api_key
        )

    flow_data: dict[str, pd.DataFrame | None] = {}
    for name in names:
        try:
            flow_data[name.key] = fetch_investor_flow(
                name.krx_code, name.key, cfg["data"]["flow_lookback_days"], cache_dir
            )
        except RuntimeError as error:
            # KRX/pykrx does not expose per-ticker investor-value breakdowns for ETFs
            # (confirmed live for KODEX 200 / 069500 during pilot prep) — same expected
            # asymmetry as the missing DART channel for ETFs, not a pipeline bug.
            print(f"[WARN] investor-flow unavailable for {name.key} ({name.krx_code}): {error}")
            flow_data[name.key] = None

    reference_ticker = names[0].yf_ticker
    window = 2 if args.sanity else cfg["windows"]["decision_window_days"]
    dates = decision_dates(price_data[reference_ticker], window)

    cells = [tuple(cfg["cells"][0])] if args.sanity else [tuple(c) for c in cfg["cells"]]

    start_time = time.time()
    results: dict[str, dict] = {}
    for diet, scaffold in cells:
        cell_key = f"{diet}_{scaffold}"
        per_name, sample_traces = run_cell(diet, scaffold, names, price_data, dart_filings, flow_data, dates, cfg)

        next_day_returns = {ticker: daily_returns(df) for ticker, df in price_data.items()}
        backtest_result = run_backtest(
            per_name,
            {name.yf_ticker: next_day_returns[name.yf_ticker] for name in names},
            cfg["execution"]["transaction_cost_bps"],
        )
        results[cell_key] = {
            "cumulative_return": backtest_result.cumulative_return,
            "annualized_sharpe": backtest_result.annualized_sharpe,
            "max_drawdown": backtest_result.max_drawdown,
            "parse_failure_rate": backtest_result.parse_failure_rate,
            "n_decisions": backtest_result.n_decisions,
            "n_llm_calls": backtest_result.n_llm_calls,
            "sample_traces": sample_traces,
        }
        print(f"[{cell_key}] {results[cell_key]}", flush=True)

    elapsed_s = time.time() - start_time

    benchmark = compute_buy_and_hold(names, price_data, dates)
    print(f"[benchmark] {benchmark}", flush=True)

    delta_data_s0 = results.get("D5_S0", {}).get("cumulative_return", float("nan")) - results.get(
        "D1_S0", {}
    ).get("cumulative_return", float("nan"))
    delta_scaffold_d1 = results.get("D1_S3", {}).get("cumulative_return", float("nan")) - results.get(
        "D1_S0", {}
    ).get("cumulative_return", float("nan"))
    delta_scaffold_d5 = results.get("D5_S3", {}).get("cumulative_return", float("nan")) - results.get(
        "D5_S0", {}
    ).get("cumulative_return", float("nan"))

    output = {
        "seed": seed,
        "sanity_mode": args.sanity,
        "decision_window_days": len(dates),
        "start_date": str(dates[0].date()) if dates else None,
        "end_date": str(dates[-1].date()) if dates else None,
        "elapsed_seconds": elapsed_s,
        "results": results,
        "benchmark": benchmark,
        "derived": {
            "delta_data_at_s0": delta_data_s0,
            "delta_scaffold_at_d1": delta_scaffold_d1,
            "delta_scaffold_at_d5": delta_scaffold_d5,
            "note": "cumulative-return deltas at pilot scale (1 seed, tiny sample) — diagnostic only, not statistically powered",
        },
    }

    results_dir = HERE / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    out_name = f"seed_{seed}_sanity.json" if args.sanity else f"seed_{seed}.json"
    with open(results_dir / out_name, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, ensure_ascii=False)

    print(f"\nWrote results to {results_dir / out_name}")


if __name__ == "__main__":
    main()

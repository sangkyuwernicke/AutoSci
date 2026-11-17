"""Deterministic walk-forward backtest executor for the pilot's single-agent (O0) decisions.

Pilot Spec: experiments/pilot/global-linkage-channel-ablation-blanket-index.yaml

Decisions made using information known at the close of day t are executed against
the close-to-close return from day t to day t+1 (standard next-bar execution, no
look-ahead). Equal-weight, long-only across the pilot universe.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from agent import AgentDecision

TRADING_DAYS_PER_YEAR = 252


@dataclass
class NameDecisionSeries:
    name: str
    dates: list[pd.Timestamp]
    decisions: list[AgentDecision]


@dataclass
class BacktestResult:
    cumulative_return: float
    annualized_sharpe: float
    max_drawdown: float
    directional_hit_rate: float
    parse_failure_rate: float
    n_decisions: int
    daily_portfolio_returns: list[float] = field(default_factory=list)


def _weights_from_decisions(decisions: list[AgentDecision]) -> list[float]:
    weights: list[float] = []
    previous = 0.0
    for decision in decisions:
        if decision.action == "HOLD":
            weights.append(previous)
        else:
            weights.append(decision.position_fraction)
        previous = weights[-1]
    return weights


def run_backtest(
    per_name: dict[str, NameDecisionSeries],
    next_day_returns: dict[str, pd.Series],
    transaction_cost_bps: float,
) -> BacktestResult:
    """Combine per-name decisions into an equal-weight, long-only portfolio backtest."""
    names = list(per_name.keys())
    n_days = len(per_name[names[0]].dates)

    weight_matrix = np.zeros((n_days, len(names)))
    return_matrix = np.zeros((n_days, len(names)))
    all_decisions: list[AgentDecision] = []
    all_hit_flags: list[bool] = []

    for col, name in enumerate(names):
        series = per_name[name]
        weights = _weights_from_decisions(series.decisions)
        weight_matrix[:, col] = weights
        all_decisions.extend(series.decisions)

        for row, (date, decision) in enumerate(zip(series.dates, series.decisions)):
            ret = float(next_day_returns[name].asof(date))
            return_matrix[row, col] = ret if pd.notna(ret) else 0.0
            if decision.action == "BUY" and decision.parse_ok:
                all_hit_flags.append(ret > 0)
            elif decision.action == "SELL" and decision.parse_ok:
                all_hit_flags.append(ret < 0)

    gross_daily = (weight_matrix * return_matrix).mean(axis=1)

    weight_changes = np.vstack([weight_matrix[0], np.diff(weight_matrix, axis=0)])
    turnover = np.abs(weight_changes).mean(axis=1)
    cost = turnover * (transaction_cost_bps / 10_000.0)

    net_daily = gross_daily - cost
    equity_curve = np.cumprod(1 + net_daily)

    cumulative_return = float(equity_curve[-1] - 1.0)
    daily_std = float(np.std(net_daily, ddof=1)) if len(net_daily) > 1 else 0.0
    sharpe = float(np.mean(net_daily) / daily_std * np.sqrt(TRADING_DAYS_PER_YEAR)) if daily_std > 0 else 0.0

    running_max = np.maximum.accumulate(equity_curve)
    drawdown = (equity_curve - running_max) / running_max
    max_drawdown = float(drawdown.min())

    hit_rate = float(np.mean(all_hit_flags)) if all_hit_flags else float("nan")
    parse_failure_rate = float(np.mean([not d.parse_ok for d in all_decisions]))

    return BacktestResult(
        cumulative_return=cumulative_return,
        annualized_sharpe=sharpe,
        max_drawdown=max_drawdown,
        directional_hit_rate=hit_rate,
        parse_failure_rate=parse_failure_rate,
        n_decisions=len(all_decisions),
        daily_portfolio_returns=net_daily.tolist(),
    )

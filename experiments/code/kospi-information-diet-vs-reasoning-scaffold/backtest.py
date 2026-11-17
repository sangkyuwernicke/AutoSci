"""Deterministic walk-forward backtest executor for one cell's (name x day) decisions.

Pilot Spec: experiments/pilot/kospi-information-diet-vs-reasoning-scaffold.yaml

Decisions made using information known at the close of day t are executed against
the close-to-close return from day t to day t+1 (standard next-bar execution, no
look-ahead). Equal-weight, long-only across the pilot universe.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from agents import AgentDecision

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
    parse_failure_rate: float
    n_decisions: int
    n_llm_calls: int
    daily_portfolio_returns: list[float] = field(default_factory=list)


def _weights_from_decisions(decisions: list[AgentDecision]) -> list[float]:
    """Each day's target weight is `position_fraction` directly, for every action label.

    The agent prompts (S0_SYSTEM, TRADER_SYSTEM, RISK_MANAGER_SYSTEM in agents.py)
    define position_fraction as "the target fraction ... to hold" regardless of
    action — action is a descriptive label, not a separate instruction to ignore
    the fraction. An earlier version of this function special-cased HOLD to carry
    forward the *previous day's realized weight* instead of using the fraction,
    which silently zeroed out any name whose very first decision was HOLD (previous
    defaults to 0.0) even when the agent's stated target fraction was nonzero —
    caught live during pilot debugging (D5_S0 came back as an exact 0.0 across the
    whole cell). Fixed by using position_fraction uniformly.
    """
    return [decision.position_fraction for decision in decisions]


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

    for col, name in enumerate(names):
        series = per_name[name]
        weights = _weights_from_decisions(series.decisions)
        weight_matrix[:, col] = weights
        all_decisions.extend(series.decisions)

        for row, (date, _decision) in enumerate(zip(series.dates, series.decisions)):
            ret = float(next_day_returns[name].asof(date))
            return_matrix[row, col] = ret if pd.notna(ret) else 0.0

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

    parse_failure_rate = float(np.mean([not d.parse_ok for d in all_decisions]))
    n_llm_calls = int(sum(d.n_llm_calls for d in all_decisions))

    return BacktestResult(
        cumulative_return=cumulative_return,
        annualized_sharpe=sharpe,
        max_drawdown=max_drawdown,
        parse_failure_rate=parse_failure_rate,
        n_decisions=len(all_decisions),
        n_llm_calls=n_llm_calls,
        daily_portfolio_returns=net_daily.tolist(),
    )

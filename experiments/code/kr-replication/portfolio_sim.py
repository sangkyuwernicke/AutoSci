"""Portfolio simulator for the TradingAgents Korea replication (Stage 1).

Turns the per-decision ratings in one or more TradingAgents memory logs into a
long-only equal-weight portfolio and compares it with simple baselines.

Rules (fixed before looking at results, see kr-tradingagents-replication-spec.md):
  * Buy / Overweight  -> 100% long in that name
  * Hold              -> keep the previous position
  * Underweight/Sell  -> cash
  * A decision dated d is executed at the NEXT trading day's open.
  * Cost: --cost-bps per unit of position change (default 20 bps, as in the pilot).
  * Capital is split equally across tickers; the portfolio is rebalanced daily
    back to equal weights of *capital slots* (each ticker is an independent slot).

Usage:
  python portfolio_sim.py --logs run1/trading_memory.md run2/trading_memory.md \
      --prices-dir prices --out results.json
  python portfolio_sim.py --logs LOG --download --start 2024-01-02 --end 2026-08-31
Prices are CSVs (columns Date,Open,Close) named <TICKER>.csv, e.g. 005930.KS.csv.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

TAG = re.compile(r"^\[(\d{4}-\d{2}-\d{2}) \| ([^|]+?) \| ([^|]+?) \|", re.M)
WEIGHT = {"buy": 1.0, "overweight": 1.0, "hold": None, "underweight": 0.0, "sell": 0.0}
WEIGHT_ALT = {"buy": 1.0, "overweight": 0.5, "hold": None, "underweight": 0.0, "sell": 0.0}


def read_ratings(log_path: Path) -> pd.DataFrame:
    text = Path(log_path).read_text(encoding="utf-8")
    rows = [(pd.Timestamp(d), t.strip(), r.strip()) for d, t, r in TAG.findall(text)]
    return pd.DataFrame(rows, columns=["date", "ticker", "rating"])


def load_prices(tickers, prices_dir=None, download=False, start=None, end=None) -> dict:
    out = {}
    for t in tickers:
        p = Path(prices_dir or ".") / f"{t}.csv"
        if download:
            import yfinance as yf

            df = yf.download(t, start=start, end=end, auto_adjust=False, progress=False)
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            df = df[["Open", "Close"]].dropna()
            if prices_dir:
                Path(prices_dir).mkdir(parents=True, exist_ok=True)
                df.to_csv(p)
        else:
            df = pd.read_csv(p, index_col=0, parse_dates=True)[["Open", "Close"]].dropna()
        out[t] = df.sort_index()
    return out


def position_series(ratings: pd.DataFrame, idx: pd.DatetimeIndex, weights=WEIGHT) -> pd.Series:
    """Target position per trading day: decision at d takes effect on the next trading day."""
    pos = pd.Series(np.nan, index=idx)
    for _, row in ratings.sort_values("date").iterrows():
        w = weights.get(row["rating"].lower())
        if w is None:  # Hold or unreadable rating: no change
            continue
        later = idx[idx > row["date"]]
        if len(later):
            pos.loc[later[0]] = w
    return pos.ffill().fillna(0.0)


def slot_returns(px: pd.DataFrame, pos: pd.Series, cost_bps: float) -> pd.Series:
    """Daily return of one capital slot holding `pos` (position is applied from that day's open)."""
    prev_close = px["Close"].shift(1)
    prev_pos = pos.shift(1).fillna(0.0)
    overnight = px["Open"] / prev_close - 1.0
    intraday = px["Close"] / px["Open"] - 1.0
    ret = prev_pos * overnight + pos * intraday
    ret -= (pos - prev_pos).abs() * cost_bps / 1e4
    return ret.iloc[1:]


def buy_hold_slot(px: pd.DataFrame, cost_bps: float, enter_after=None) -> pd.Series:
    """Hold from the open of the first trading day after `enter_after` (same entry as the agent)."""
    pos = pd.Series(1.0, index=px.index)
    if enter_after is not None:
        pos[px.index <= enter_after] = 0.0
    return slot_returns(px, pos, cost_bps)


def sma_slot(px_full: pd.DataFrame, cost_bps: float, start, short=5, long=20) -> pd.Series:
    """SMA cross computed on full history (no warm-up loss), traded from the first agent date."""
    px = px_full
    sig = (px["Close"].rolling(short).mean() > px["Close"].rolling(long).mean()).astype(float)
    pos = sig.shift(1).fillna(0.0)  # signal from close t-1 -> position applied from open t
    pos[px.index <= start] = 0.0
    return slot_returns(px[px.index >= start], pos[px.index >= start], cost_bps)


def metrics(r: pd.Series) -> dict:
    r = r.dropna()
    eq = (1 + r).cumprod()
    ann = np.sqrt(252)
    dn = r[r < 0].std()
    var5 = r.quantile(0.05)
    return {
        "cum_return": float(eq.iloc[-1] - 1),
        "ann_return": float(eq.iloc[-1] ** (252 / len(r)) - 1),
        "sharpe": float(r.mean() / r.std() * ann) if r.std() > 0 else float("nan"),
        "sortino": float(r.mean() / dn * ann) if dn and dn > 0 else float("nan"),
        "mdd": float((eq / eq.cummax() - 1).min()),
        "cvar5": float(r[r <= var5].mean()),
        "n_days": int(len(r)),
    }


def sharpe(x: np.ndarray) -> float:
    s = x.std(ddof=1)
    return x.mean() / s * np.sqrt(252) if s > 0 else np.nan


def block_bootstrap_diff(a: pd.Series, b: pd.Series, block=20, n=2000, seed=0) -> dict:
    """95% CI of Sharpe(a) - Sharpe(b), moving-block bootstrap on aligned daily returns."""
    d = pd.concat([a, b], axis=1).dropna().values
    rng = np.random.default_rng(seed)
    T = len(d)
    if T < 2 * block:
        return {"point": float("nan"), "lo": float("nan"), "hi": float("nan")}
    nb = int(np.ceil(T / block))
    diffs = []
    for _ in range(n):
        starts = rng.integers(0, T - block + 1, nb)
        s = np.concatenate([d[i:i + block] for i in starts])[:T]
        diffs.append(sharpe(s[:, 0]) - sharpe(s[:, 1]))
    return {"point": float(sharpe(d[:, 0]) - sharpe(d[:, 1])),
            "lo": float(np.nanpercentile(diffs, 2.5)), "hi": float(np.nanpercentile(diffs, 97.5))}


def simulate(logs, prices, cost_bps=20.0, weights=WEIGHT, tickers=None) -> dict:
    ratings = pd.concat([read_ratings(p) for p in logs], ignore_index=True)
    tickers = tickers or sorted(ratings["ticker"].unique())
    agent, bh, sma = {}, {}, {}
    for t in tickers:
        px_full = prices[t]
        pos_full = position_series(ratings[ratings["ticker"] == t], px_full.index, weights)
        # the clock starts at the first decision; all strategies enter no earlier than the next open
        start = ratings.loc[ratings["ticker"] == t, "date"].min()
        px = px_full[px_full.index >= start]
        agent[t] = slot_returns(px, pos_full.loc[px.index], cost_bps)
        bh[t] = buy_hold_slot(px, cost_bps, enter_after=start)
        sma[t] = sma_slot(px_full, cost_bps, start)
    ew = lambda d: pd.DataFrame(d).mean(axis=1).dropna()
    series = {"agent": ew(agent), "buy_hold_ew": ew(bh), "sma_5_20_ew": ew(sma)}
    out = {k: metrics(v) for k, v in series.items()}
    out["sharpe_diff_vs_buy_hold"] = block_bootstrap_diff(series["agent"], series["buy_hold_ew"])
    out["sharpe_diff_vs_sma"] = block_bootstrap_diff(series["agent"], series["sma_5_20_ew"])
    out["n_decisions"] = int(len(ratings))
    out["rating_counts"] = ratings["rating"].str.lower().value_counts().to_dict()
    out["tickers"] = tickers
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--logs", nargs="+", required=True, help="memory logs (one per seed/run)")
    ap.add_argument("--prices-dir", default="prices")
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--cost-bps", type=float, default=20.0)
    ap.add_argument("--alt-weights", action="store_true", help="Overweight = 50%")
    ap.add_argument("--out", default="results.json")
    a = ap.parse_args()
    ratings = pd.concat([read_ratings(Path(p)) for p in a.logs])
    tickers = sorted(ratings["ticker"].unique())
    prices = load_prices(tickers, a.prices_dir, a.download, a.start, a.end)
    res = []
    for log in a.logs:  # one result per seed
        res.append(simulate([Path(log)], prices, a.cost_bps, WEIGHT_ALT if a.alt_weights else WEIGHT))
    Path(a.out).write_text(json.dumps(res, indent=2, ensure_ascii=False))
    for log, r in zip(a.logs, res):
        print(log)
        for k in ("agent", "buy_hold_ew", "sma_5_20_ew"):
            m = r[k]
            print(f"  {k:12s} cum {m['cum_return']:+.1%}  sharpe {m['sharpe']:.2f}  mdd {m['mdd']:.1%}")
        d = r["sharpe_diff_vs_buy_hold"]
        print(f"  Sharpe diff vs buy&hold: {d['point']:+.2f} [{d['lo']:+.2f}, {d['hi']:+.2f}]")


if __name__ == "__main__":
    main()

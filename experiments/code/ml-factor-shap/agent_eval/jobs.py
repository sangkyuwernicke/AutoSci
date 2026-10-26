"""Plan which (stock, month-end) decisions to request, run them resumably, and turn them into model predictions."""
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from agent_eval.backends import RATING_SCORE


def plan_jobs(panel, store, test_start, test_end, n_stocks, select="top_mcap", seed=0, repeats=1):
    """panel: output of features.add_target (needs date, ticker, label_year). Returns jobs sorted chronologically.

    Stocks must be present in >= 90 % of the test months so that every month has the same cross-section; they are
    the n largest by mean market cap over the test window (select="top_mcap") or a seeded random draw."""
    t = panel[(panel["label_year"] >= test_start) & (panel["label_year"] <= test_end)]
    if t.empty:
        raise SystemExit("no panel rows in the requested test window")
    months = sorted(t["date"].unique())
    cover = t.groupby("ticker")["date"].nunique()
    ok = cover[cover >= 0.9 * len(months)].index
    if len(ok) == 0:
        raise SystemExit("no ticker covers 90 % of the test months")
    if select == "random":
        picked = sorted(np.random.default_rng(seed).choice(sorted(ok), size=min(n_stocks, len(ok)), replace=False))
    else:
        mc = store.prices[store.prices["ticker"].isin(ok) & store.prices["date"].isin(months)]
        picked = list(mc.groupby("ticker")["mcap"].mean().nlargest(n_stocks).index)
    sel = t[t["ticker"].isin(picked)][["ticker", "date", "label_year"]].drop_duplicates()
    jobs = pd.concat([sel.assign(repeat=r) for r in range(repeats)], ignore_index=True)
    jobs["date"] = pd.to_datetime(jobs["date"])
    return jobs.sort_values(["date", "ticker", "repeat"]).reset_index(drop=True)


def load_decisions(path):
    recs = {}
    p = Path(path)
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                recs[(r["ticker"], r["date"], r["repeat"])] = r         # later lines win (retries)
    return recs


def run_jobs(jobs, backend, out_dir, max_jobs=None, shard=(0, 1), retry_errors=False, max_consecutive_errors=5,
             log=print):
    """Append one JSON line per decision to <out_dir>/decisions.jsonl; skip finished jobs (resumable)."""
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    path = out / "decisions.jsonl"
    done = load_decisions(path)
    todo = []
    for i, r in jobs.iterrows():
        if i % shard[1] != shard[0]:
            continue
        key = (r["ticker"], r["date"].strftime("%Y-%m-%d"), int(r["repeat"]))
        prev = done.get(key)
        if prev is not None and (prev.get("rating") or not retry_errors):
            continue
        todo.append(key)
    if max_jobs:
        todo = todo[:max_jobs]
    log(f"[agents] {len(todo)} jobs to run ({len(done)} already recorded, backend={backend.name})")
    t0, errs = time.time(), 0
    for n, (code, date, rep) in enumerate(todo, 1):
        s = time.time()
        rec = {"ticker": code, "date": date, "repeat": rep, "backend": backend.name}
        try:
            rating, meta = backend.decide(code, date, rep)
            rec.update(rating=rating, **meta)
            errs = 0
        except KeyboardInterrupt:
            log("[agents] interrupted; finished jobs are saved, rerun to resume")
            break
        except Exception as exc:                                  # one bad job must not lose the others
            rec.update(rating=None, error=f"{type(exc).__name__}: {exc}"[:500])
            errs += 1
        rec["seconds"] = round(time.time() - s, 1)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if n % 5 == 0 or n == len(todo):
            el = time.time() - t0
            log(f"[agents] {n}/{len(todo)} done, {el / n:.0f}s/job, ~{el / n * (len(todo) - n) / 60:.0f} min left")
        if errs >= max_consecutive_errors:
            log(f"[agents] {errs} consecutive failures (last: {rec.get('error')}); stopping. Check keys/network, "
                "then rerun with --retry-errors")
            break
    return load_decisions(path)


def decisions_to_predictions(decisions, panel, tie_seed=0, model="tradingagents", fset="agent"):
    """decisions: dict from load_decisions. Rating -> score (Buy=2 ... Sell=-2), repeats averaged.

    REVIEW (unparseable) and failed jobs are dropped and counted. The 5-level scale makes ties inevitable, so the
    final score adds a seeded random jitter far below one rating step: ties are broken at random, not by any
    information. `score_raw` keeps the rating average."""
    rows = []
    for r in decisions.values():
        sc = RATING_SCORE.get(r.get("rating"))
        rows.append({"ticker": r["ticker"], "date": pd.Timestamp(r["date"]), "score_raw": sc})
    d = pd.DataFrame(rows)
    stats = {"jobs": len(d), "failed_or_review": int(d["score_raw"].isna().sum())} if len(d) else {"jobs": 0}
    d = d.dropna(subset=["score_raw"]).groupby(["ticker", "date"], as_index=False)["score_raw"].mean()
    keep = panel[["date", "ticker", "y", "ret_next", "mkt_next", "label_year"]]
    m = d.merge(keep, on=["ticker", "date"], how="inner")
    rng = np.random.default_rng(tie_seed)
    m["score"] = m["score_raw"] + rng.uniform(0, 1e-3, len(m))
    m = m.rename(columns={"label_year": "test_year"})
    m["model"], m["fset"] = model, fset
    stats["stock_months"] = len(m)
    return m[["date", "ticker", "y", "ret_next", "mkt_next", "score", "score_raw", "model", "fset", "test_year"]], stats

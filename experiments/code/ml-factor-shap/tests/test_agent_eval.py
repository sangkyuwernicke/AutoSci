"""Agent adapter tests. Offline parts need only numpy/pandas; the router test runs when `tradingagents` is installed.
Run: python tests/test_agent_eval.py"""
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_eval.backends import RATING_SCORE, MockBackend
from agent_eval.jobs import decisions_to_predictions, load_decisions, plan_jobs, run_jobs
from agent_eval.store import PointInTimeStore, code_from_symbol

rng = np.random.default_rng(0)
MONTHS = pd.date_range("2020-01-31", "2023-12-31", freq="ME")
TICKERS = {"000010": "KOSPI", "000020": "KOSPI", "000030": "KOSDAQ"}
MACRO = ["BASE_RATE", "TERM_SPREAD", "CPI_YOY", "KRWUSD", "VKOSPI"]


def make_raw(raw):
    rows = []
    for t, mk in TICKERS.items():
        px = 100 * np.cumprod(1 + rng.normal(0.005, 0.05, len(MONTHS)))
        for k, m in enumerate(MONTHS):
            rows.append(dict(date=m, ticker=t, name=f"기업{t}", market=mk, close=px[k], shares=1e6,
                             mcap=px[k] * 1e6 * (1 + (t == "000010")), ret1=np.nan if k == 0 else px[k] / px[k - 1] - 1,
                             adj_close=px[k], seg=1, eligible=True))
    pd.DataFrame(rows).to_parquet(raw / "prices_monthly.parquet")
    q = pd.date_range("2019-03-31", "2023-12-31", freq="QE")
    fr = []
    for t in TICKERS:
        f = pd.DataFrame(dict(ticker=t, period_end=q, filing_date=q + pd.Timedelta(days=45)))
        for c in ["sales", "gross_profit", "op_income", "net_income", "cfo", "interest_expense"]:
            f[c] = np.arange(len(q)) + 1.0                       # strictly increasing: value identifies the quarter
        for c in ["equity", "assets", "liabilities", "current_assets", "current_liabilities", "inventory", "cash",
                  "debt"]:
            f[c] = 100.0
        fr.append(f)
    pd.concat(fr).to_parquet(raw / "fundamentals.parquet")
    mo = pd.date_range("2019-01-31", "2023-12-31", freq="ME")
    pd.concat([pd.DataFrame(dict(name=n, avail_date=mo + pd.Timedelta(days=5), value=np.arange(len(mo), dtype=float)))
               for n in MACRO]).to_parquet(raw / "macro.parquet")


with tempfile.TemporaryDirectory() as tmp:
    raw = Path(tmp) / "raw"; raw.mkdir(); make_raw(raw)
    store = PointInTimeStore(raw)

    # ---- symbols
    assert code_from_symbol("005930.KS") == "005930" and code_from_symbol("5930") == "005930"
    assert store.yahoo_symbol("000010") == "000010.KS" and store.yahoo_symbol("000030") == "000030.KQ"

    # ---- prices: nothing after asof
    txt = store.price_table("000010", "2021-01-01", "2021-06-30")
    assert "2021-06-30" in txt and "2021-07-31" not in txt and "no daily" in txt
    try:
        store.price_table("000010", "2019-01-01", "2019-12-31"); raise AssertionError("expected LookupError")
    except LookupError:
        pass

    # ---- fundamentals are point in time (filing date, not period end)
    q = pd.date_range("2019-03-31", "2023-12-31", freq="QE")
    idx = list(q).index(pd.Timestamp("2020-12-31"))              # filed 2021-02-14
    before = store.fundamentals_text("000010", "2021-02-13")     # Q4-2020 not yet filed
    after = store.fundamentals_text("000010", "2021-02-14")
    assert "latest_filed_period_end: 2020-09-30" in before and "latest_filed_period_end: 2020-12-31" in after
    f2 = pd.read_parquet(raw / "fundamentals.parquet")
    f2.loc[f2["filing_date"] > "2021-02-14", ["sales", "net_income", "equity"]] = 9e9   # rewrite the future
    f2.to_parquet(raw / "fundamentals.parquet")
    assert PointInTimeStore(raw).fundamentals_text("000010", "2021-02-14") == after, "future filings must not leak"
    st = store.statement_text("000010", "income", "quarterly", "2021-06-30")
    assert st.count("\n") >= 6 and "2021-05-15" in st and "2021-08-14" not in st
    try:
        store.fundamentals_text("000010", "2019-01-01"); raise AssertionError("expected LookupError")
    except LookupError:
        pass

    # ---- macro: public-by-asof only, aliases, unknown indicator
    m = store.macro_text("vix", "2021-03-31", 90)
    assert "VKOSPI" in m and "public on or before 2021-03-31" in m
    obs = pd.read_parquet(raw / "macro.parquet")
    allowed = obs[(obs["name"] == "VKOSPI") & (obs["avail_date"] <= "2021-03-31")]["value"].max()
    assert f"latest: {allowed:,.4f}" in m
    assert store.macro_text("nonsense", "2021-03-31").startswith("NO_DATA_AVAILABLE")

    # ---- indicators
    ind = store.indicators_text("000010", "2021-06-30", "rsi")
    assert "return_3m" in ind and "Daily indicators" in ind

    # ---- job planning, resumable run, error handling, sharding
    panel = pd.DataFrame([dict(date=d, ticker=t, label_year=(d + pd.offsets.MonthEnd(1)).year, y=int(rng.random() > .5),
                               ret_next=rng.normal(0, .05), mkt_next=0.0)
                          for d in MONTHS for t in TICKERS])
    jobs = plan_jobs(panel, store, 2022, 2022, n_stocks=2, select="top_mcap", repeats=2)
    assert len(set(jobs["ticker"])) == 2
    assert "000010" in set(jobs["ticker"]), "largest market cap must be selected"
    assert jobs["label_year"].eq(2022).all() and jobs["date"].is_monotonic_increasing
    assert len(jobs) == 2 * jobs["date"].nunique() * 2

    out = Path(tmp) / "run"
    logs = []
    dec = run_jobs(jobs, MockBackend(seed=1), out, log=logs.append)
    assert len(dec) == len(jobs) and all(r["rating"] in RATING_SCORE for r in dec.values())
    n_lines = len((out / "decisions.jsonl").read_text().splitlines())
    run_jobs(jobs, MockBackend(seed=1), out, log=logs.append)
    assert len((out / "decisions.jsonl").read_text().splitlines()) == n_lines, "finished jobs must not rerun"

    class Flaky:
        name = "flaky"
        def __init__(self): self.calls = 0
        def decide(self, code, date, repeat):
            self.calls += 1
            if self.calls <= 2:
                raise RuntimeError("API down")
            return "Hold", {}
    out2 = Path(tmp) / "run2"
    fl = Flaky()
    d2 = run_jobs(jobs, fl, out2, max_jobs=4, log=logs.append)
    assert sum(1 for r in d2.values() if r["rating"] is None) == 2 and "API down" in json.dumps(list(d2.values()))
    run_jobs(jobs, fl, out2, max_jobs=10, log=logs.append)          # errors are not retried by default
    assert sum(1 for r in load_decisions(out2 / "decisions.jsonl").values() if r["rating"] is None) == 2
    d3 = run_jobs(jobs, fl, out2, retry_errors=True, max_jobs=10, log=logs.append)
    assert sum(1 for r in d3.values() if r["rating"] is None) == 0

    class Dead:
        name = "dead"
        def decide(self, *a): raise RuntimeError("bad key")
    d4 = run_jobs(jobs, Dead(), Path(tmp) / "run3", log=logs.append)
    assert len(d4) == 5 and any("consecutive failures" in s for s in logs), "must stop after repeated failures"

    sh = [len(run_jobs(jobs, MockBackend(), Path(tmp) / f"s{i}", shard=(i, 3), log=logs.append)) for i in range(3)]
    assert sum(sh) == len(jobs)

    # ---- decisions -> predictions
    recs = {("000010", "2022-01-31", 0): dict(ticker="000010", date="2022-01-31", repeat=0, rating="Buy"),
            ("000010", "2022-01-31", 1): dict(ticker="000010", date="2022-01-31", repeat=1, rating="Hold"),
            ("000020", "2022-01-31", 0): dict(ticker="000020", date="2022-01-31", repeat=0, rating="REVIEW"),
            ("000030", "2022-01-31", 0): dict(ticker="000030", date="2022-01-31", repeat=0, rating="Sell")}
    pred, stats = decisions_to_predictions(recs, panel, tie_seed=3)
    assert stats["failed_or_review"] == 1 and len(pred) == 2
    p10 = pred[pred["ticker"] == "000010"].iloc[0]
    assert p10["score_raw"] == 1.0 and 1.0 <= p10["score"] < 1.001, "repeats are averaged, jitter << one rating step"
    assert pred["model"].eq("tradingagents").all() and {"y", "ret_next", "mkt_next", "test_year"} <= set(pred.columns)
    pred2, _ = decisions_to_predictions(recs, panel, tie_seed=3)
    assert (pred["score"].to_numpy() == pred2["score"].to_numpy()).all(), "tie-break must be reproducible"

    # ---- permutation baseline: a planted signal is flagged, shuffled scores are not (needs scikit-learn)
    try:
        import sklearn  # noqa: F401
        import compare_agent as ca
        big = pd.DataFrame([dict(date=d, ticker=f"{i:06d}", y=0, ret_next=rng.normal(0, .05), mkt_next=0.0, label_year=2022)
                            for d in MONTHS[:24] for i in range(30)])
        big["y"] = (big["ret_next"] > big.groupby("date")["ret_next"].transform("quantile", 0.8)).astype(int)
        good = big.assign(score=big["ret_next"] + rng.normal(0, .03, len(big)))
        junk = big.assign(score=rng.normal(size=len(big)))
        g, j = ca.null_test(good, 0.2, 100), ca.null_test(junk, 0.2, 100)
        assert g["p_perm_auc"] < 0.05 and abs(g["auc_null_mean"] - 0.5) < 0.03
        assert j["p_perm_auc"] > 0.01 and j["auc_null_p95"] > 0.5
    except ImportError:
        pass

    # ---- against the real TradingAgents router, if installed
    try:
        import tradingagents  # noqa: F401
        have_ta = True
    except ImportError:
        have_ta = False
    if have_ta:
        from tradingagents.dataflows import router
        from tradingagents.dataflows.config import set_config
        from tradingagents.default_config import DEFAULT_CONFIG
        from agent_eval import vendor

        cfg_over = vendor.install(store)
        cfg = dict(DEFAULT_CONFIG); cfg["data_vendors"] = {**DEFAULT_CONFIG["data_vendors"], **cfg_over["data_vendors"]}
        cfg["tool_vendors"] = {}
        set_config(cfg)
        for k in ["llm_provider", "deep_think_llm", "quick_think_llm", "max_debate_rounds", "max_risk_discuss_rounds",
                  "output_language", "checkpoint_enabled", "data_vendors", "tool_vendors", "memory_log_path",
                  "data_cache_dir", "results_dir"]:
            assert k in DEFAULT_CONFIG, f"TradingAgents config no longer has {k!r}"
        r = router.route_to_vendor
        assert "Fundamentals for 000010" in r("get_fundamentals", "000010.KS", "2021-06-30")
        assert "latest_filed_period_end: 2020-12-31" in r("get_fundamentals", "000010.KS", "2021-02-14")
        assert "Month-end prices" in r("get_stock_data", "000010.KS", "2021-01-01", "2021-06-30")
        assert "Month-frequency" in r("get_indicators", "000010.KS", "rsi", "2021-06-30", 30)
        for fn, kind in [("get_income_statement", "income"), ("get_balance_sheet", "balance"), ("get_cashflow", "cashflow")]:
            assert f"{kind} statement" in r(fn, "000010.KS", "quarterly", "2021-06-30")
        assert "VKOSPI" in r("get_macro_indicators", "vix", "2021-06-30", None)
        for fn, args in [("get_news", ("000010.KS", "2021-05-01", "2021-06-30")), ("get_global_news", ("2021-06-30", 7, 10)),
                         ("get_insider_transactions", ("000010.KS", "2021-06-30"))]:
            assert "NO_DATA_AVAILABLE" in r(fn, *args), fn
        assert "NO_DATA_AVAILABLE" in r("get_fundamentals", "999999.KS", "2021-06-30")
        # the snapshot tool imported the Yahoo implementation by name; it must now be ours
        import tradingagents.agents.tools as ta_tools
        assert "Month-frequency" in ta_tools.build_verified_market_snapshot("000010.KS", "2021-06-30", 30)
print("agent adapter tests passed" + ("" if have_ta else " (TradingAgents not installed: router test skipped)"))

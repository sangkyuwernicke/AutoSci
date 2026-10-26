"""Decision backends: the real TradingAgents graph, and a deterministic offline stand-in for tests."""
import copy
import hashlib
import shutil
from pathlib import Path

RATING_SCORE = {"Buy": 2.0, "Overweight": 1.0, "Hold": 0.0, "Underweight": -1.0, "Sell": -2.0}


class MockBackend:
    """No LLM, no information about the future: a hash of (ticker, date, repeat) picks one of the five ratings.
    Used by tests and `--dry-run` style checks of the plumbing; its expected AUC is 0.5."""
    name = "mock"

    def __init__(self, store=None, seed=0):
        self.seed = seed

    def decide(self, code, date, repeat):
        h = int(hashlib.sha256(f"{self.seed}|{code}|{date}|{repeat}".encode()).hexdigest(), 16)
        return list(RATING_SCORE)[h % 5], {}


class TradingAgentsBackend:
    """One TradingAgentsGraph per (ticker, date, repeat) so that nothing carries over between decisions.

    Why a fresh graph each time: TradingAgents keeps a persistent memory log of past decisions and feeds lessons
    from *settled* outcomes into the next run. In a backtest that memory would contain realised future returns
    for any job processed out of chronological order (or in parallel shards). Each job therefore gets an empty
    memory file and its own checkpoint/cache directory, deleted afterwards.
    """
    name = "tradingagents"

    def __init__(self, store, work_dir, llm_provider="openai", deep_model=None, quick_model=None,
                 analysts=("market", "fundamentals"), debate_rounds=1, risk_rounds=1, language="English",
                 extra_config=None):
        from agent_eval import vendor
        self.store = store
        self.work_dir = Path(work_dir)
        self.analysts = list(analysts)
        self.vendor_cfg = vendor.install(store)
        try:
            from tradingagents.default_config import DEFAULT_CONFIG
        except ImportError as exc:                              # pragma: no cover
            raise SystemExit("TradingAgents is not installed: pip install "
                             "git+https://github.com/TauricResearch/TradingAgents.git") from exc
        cfg = copy.deepcopy(DEFAULT_CONFIG)
        cfg["llm_provider"] = llm_provider
        if deep_model:
            cfg["deep_think_llm"] = deep_model
        if quick_model:
            cfg["quick_think_llm"] = quick_model
        cfg["max_debate_rounds"] = debate_rounds
        cfg["max_risk_discuss_rounds"] = risk_rounds
        cfg["output_language"] = language
        cfg["checkpoint_enabled"] = False
        cfg["data_vendors"] = {**cfg.get("data_vendors", {}), **self.vendor_cfg["data_vendors"]}
        cfg["tool_vendors"] = {}
        cfg.update(extra_config or {})
        self.base_config = cfg

    def decide(self, code, date, repeat):
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        job = self.work_dir / "jobs" / f"{code}_{date}_{repeat}"
        job.mkdir(parents=True, exist_ok=True)
        cfg = copy.deepcopy(self.base_config)
        cfg["memory_log_path"] = str(job / "memory.md")
        cfg["data_cache_dir"] = str(job / "cache")
        cfg["results_dir"] = str(self.work_dir / "ta_logs")
        try:
            graph = TradingAgentsGraph(selected_analysts=self.analysts, debug=False, config=cfg)
            state, signal = graph.propagate(self.store.yahoo_symbol(code), date)
            text = ""
            if isinstance(state, dict):
                text = str(state.get("final_trade_decision", ""))[:2000]
            return str(signal), {"decision_text": text}
        finally:
            shutil.rmtree(job, ignore_errors=True)

"""Plug the point-in-time store into TradingAgents as a data vendor called "autosci".

TradingAgents routes every tool call through `tradingagents.dataflows.router.VENDOR_METHODS[method][vendor]` and has
no public registration API, so `install()` inserts our functions into that dict at run time (checked against
TradingAgents v0.7.0) and returns the config entries that make the router choose them.  The tool wrappers in
`tradingagents.agents.tools` already clamp dates to the run's trade_date; the store clamps again.

News, social and insider data do not exist in this dataset: those tools raise NoMarketDataError, which the router turns
into a NO_DATA_AVAILABLE message for the agent. Run with analysts ("market", "fundamentals") only.
"""
from agent_eval.store import PointInTimeStore, code_from_symbol

VENDOR = "autosci"
CATEGORIES = ["core_stock_apis", "technical_indicators", "fundamental_data", "news_data", "macro_data"]


def make_functions(store: PointInTimeStore, no_data_error):
    """name -> callable with the exact positional signatures used by tradingagents.agents.tools."""

    def guard(method, symbol_arg=0):
        def deco(fn):
            def wrapped(*args, **kwargs):
                try:
                    return fn(*args, **kwargs)
                except LookupError as exc:
                    sym = str(args[symbol_arg]) if len(args) > symbol_arg else ""
                    raise no_data_error(sym, detail=str(exc))
            wrapped.__name__ = f"autosci_{method}"
            return wrapped
        return deco

    @guard("get_stock_data")
    def get_stock_data(symbol, start_date, end_date, *a, **k):
        return store.price_table(code_from_symbol(symbol), start_date, end_date)

    @guard("get_indicators")
    def get_indicators(symbol, indicator, curr_date, look_back_days=30, *a, **k):
        return store.indicators_text(code_from_symbol(symbol), curr_date, indicator)

    @guard("get_fundamentals")
    def get_fundamentals(ticker, curr_date=None, *a, **k):
        return store.fundamentals_text(code_from_symbol(ticker), curr_date)

    def statement(kind, method):
        @guard(method)
        def fn(ticker, freq="quarterly", curr_date=None, *a, **k):
            return store.statement_text(code_from_symbol(ticker), kind, freq, curr_date)
        return fn

    def no_news(method, symbol_arg=0):
        @guard(method, symbol_arg)
        def fn(*a, **k):
            raise LookupError("this dataset has no news, social or insider data (KRX / DART / ECOS only)")
        return fn

    @guard("get_macro_indicators", symbol_arg=0)
    def get_macro_indicators(indicator, curr_date, look_back_days=None, *a, **k):
        return store.macro_text(indicator, curr_date, look_back_days)

    return {
        "get_stock_data": get_stock_data, "get_indicators": get_indicators,
        "get_fundamentals": get_fundamentals,
        "get_balance_sheet": statement("balance", "get_balance_sheet"),
        "get_cashflow": statement("cashflow", "get_cashflow"),
        "get_income_statement": statement("income", "get_income_statement"),
        "get_news": no_news("get_news"), "get_global_news": no_news("get_global_news"),
        "get_insider_transactions": no_news("get_insider_transactions"),
        "get_macro_indicators": get_macro_indicators,
    }


def install(store: PointInTimeStore):
    """Register the vendor and return {"data_vendors": {...}} to merge into the TradingAgents config."""
    try:
        from tradingagents.agents import tools as ta_tools
        from tradingagents.dataflows import router
        from tradingagents.dataflows.errors import NoMarketDataError
    except ImportError as exc:                                  # pragma: no cover - environment dependent
        raise SystemExit("TradingAgents is not installed in this environment: pip install "
                         "git+https://github.com/TauricResearch/TradingAgents.git") from exc

    for method, fn in make_functions(store, NoMarketDataError).items():
        if method not in router.VENDOR_METHODS:
            raise RuntimeError(f"TradingAgents has no tool {method!r}: the adapter targets v0.7.0, check the version")
        router.VENDOR_METHODS[method][VENDOR] = fn

    def snapshot(symbol, as_of_date, look_back_days=30, indicators=None):
        try:
            return store.indicators_text(code_from_symbol(symbol), as_of_date, "verified snapshot")
        except LookupError as exc:
            raise NoMarketDataError(str(symbol), detail=str(exc))

    ta_tools.build_verified_market_snapshot = snapshot          # tool imported the Yahoo version by name
    return {"data_vendors": {cat: VENDOR for cat in CATEGORIES}}

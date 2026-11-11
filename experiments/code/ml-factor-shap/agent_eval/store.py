"""Point-in-time data access for the agent adapter.

Everything is built from the files the ML pipeline already uses (data/real/*.parquet). Every query takes an `asof`
date and only returns what was public by then:
  prices        month-end snapshots with label <= asof
  fundamentals  quarterly filings with filing_date <= asof        (not period_end)
  macro         observations with avail_date <= asof
Daily OHLCV, news and social data do not exist in this dataset, so the matching tools report "no data".
"""
from pathlib import Path

import numpy as np
import pandas as pd

import data_real

MACRO_ALIASES = {
    "base_rate": "BASE_RATE", "policy_rate": "BASE_RATE", "bok_base_rate": "BASE_RATE",
    "term_spread": "TERM_SPREAD", "yield_curve": "TERM_SPREAD", "10y_minus_3y": "TERM_SPREAD",
    "cpi_yoy": "CPI_YOY", "cpi": "CPI_YOY", "inflation": "CPI_YOY",
    "krwusd": "KRWUSD", "usdkrw": "KRWUSD", "fx": "KRWUSD", "krw_usd": "KRWUSD",
    "vkospi": "VKOSPI", "vix": "VKOSPI", "volatility": "VKOSPI",
}
MACRO_TITLES = {
    "BASE_RATE": ("Bank of Korea base rate", "% p.a."),
    "TERM_SPREAD": ("Korea 10y minus 3y government bond yield", "pp"),
    "CPI_YOY": ("Korea CPI, year over year", "%"),
    "KRWUSD": ("KRW per USD", "KRW"),
    "VKOSPI": ("VKOSPI (KOSPI200 implied volatility index)", "index points"),
}


def code_from_symbol(symbol):
    """'005930.KS' / '005930.KQ' / '005930' -> '005930'."""
    return str(symbol).strip().upper().split(".")[0].zfill(6)


class PointInTimeStore:
    def __init__(self, raw_dir):
        raw = Path(raw_dir)
        self.prices = pd.read_parquet(raw / "prices_monthly.parquet")
        self.prices["date"] = pd.to_datetime(self.prices["date"])
        self.prices = self.prices.sort_values(["ticker", "date"])
        self.fund = None
        if (raw / "fundamentals.parquet").exists():
            f = pd.read_parquet(raw / "fundamentals.parquet")
            f["period_end"] = pd.to_datetime(f["period_end"])
            f["filing_date"] = pd.to_datetime(f["filing_date"])
            self.fund = data_real._fundamental_factors(f)
        self.macro = None
        if (raw / "macro.parquet").exists():
            m = pd.read_parquet(raw / "macro.parquet")
            m["avail_date"] = pd.to_datetime(m["avail_date"])
            self.macro = m.sort_values("avail_date")
        self._market = self.prices.drop_duplicates("ticker", keep="last").set_index("ticker")["market"].to_dict()

    # ---------------------------------------------------------------- symbols
    def yahoo_symbol(self, code):
        return f"{code}.{'KQ' if self._market.get(code) == 'KOSDAQ' else 'KS'}"

    def name_of(self, code):
        g = self.prices[self.prices["ticker"] == code]
        return g["name"].iloc[-1] if len(g) and "name" in g else code

    # ----------------------------------------------------------------- prices
    def _hist(self, code, asof):
        g = self.prices[(self.prices["ticker"] == code) & (self.prices["date"] <= pd.Timestamp(asof))]
        if g.empty:
            raise LookupError(f"no price history for {code} on or before {asof}")
        return g

    def price_table(self, code, start, end):
        g = self._hist(code, end)
        g = g[g["date"] >= pd.Timestamp(start)]
        if g.empty:
            raise LookupError(f"no month-end observation for {code} between {start} and {end}")
        t = g[["date", "close", "mcap", "shares", "ret1"]].copy()
        t["date"] = t["date"].dt.strftime("%Y-%m-%d")
        t = t.rename(columns={"close": "Close_KRW(unadjusted)", "mcap": "MarketCap_KRW", "shares": "Shares",
                              "ret1": "MonthlyReturn(adj)"})
        return (f"# Month-end prices for {code} ({self.name_of(code)}), {start} to {end}\n"
                "# Only month-end observations exist in this dataset (no daily open/high/low/volume).\n"
                + t.to_string(index=False, float_format=lambda x: f"{x:,.4f}"))

    def indicator_values(self, code, asof):
        g = self._hist(code, asof)
        a = g["adj_close"].to_numpy()
        seg = g["seg"].to_numpy()

        def ret(k):
            return a[-1] / a[-1 - k] - 1 if len(a) > k and seg[-1] == seg[-1 - k] else np.nan

        r1 = g["ret1"].dropna().tail(12)
        out = {
            "last_month_end": g["date"].iloc[-1].strftime("%Y-%m-%d"),
            "return_1m": ret(1), "return_3m": ret(3), "return_6m": ret(6), "return_12m": ret(12),
            "momentum_12_1": (a[-2] / a[-13] - 1) if len(a) > 12 and seg[-1] == seg[-13] else np.nan,
            "dist_to_12m_high": a[-1] / a[-12:].max() - 1 if len(a) >= 10 else np.nan,
            "sma_3m_gap": a[-1] / a[-3:].mean() - 1 if len(a) >= 3 else np.nan,
            "sma_6m_gap": a[-1] / a[-6:].mean() - 1 if len(a) >= 6 else np.nan,
            "sma_12m_gap": a[-1] / a[-12:].mean() - 1 if len(a) >= 12 else np.nan,
            "volatility_12m_ann": float(r1.std() * np.sqrt(12)) if len(r1) >= 6 else np.nan,
            "market_cap_krw": float(g["mcap"].iloc[-1]),
        }
        return out

    def indicators_text(self, code, asof, requested=""):
        v = self.indicator_values(code, asof)
        lines = [f"# Month-frequency technical summary for {code} ({self.name_of(code)}) as of {asof}",
                 "# Daily indicators (RSI, MACD, Bollinger, ATR ...) cannot be computed: only month-end closes exist."]
        if requested:
            lines.append(f"# Requested indicator(s): {requested}; the monthly summary below is returned instead.")
        for k, x in v.items():
            if isinstance(x, str):
                lines.append(f"{k}: {x}")
            elif k == "market_cap_krw":
                lines.append(f"{k}: {x:,.0f}")
            else:
                lines.append(f"{k}: {'n/a' if pd.isna(x) else f'{x:+.2%}' if k != 'volatility_12m_ann' else f'{x:.2%}'}")
        return "\n".join(lines)

    # ----------------------------------------------------------- fundamentals
    def _filed(self, code, asof, n=4):
        if self.fund is None:
            raise LookupError("fundamentals.parquet not available")
        f = self.fund[(self.fund["ticker"] == code) & (self.fund["filing_date"] <= pd.Timestamp(asof))]
        if f.empty:
            raise LookupError(f"no filed financial statements for {code} on or before {asof}")
        return f.sort_values("period_end").tail(n)

    def fundamentals_text(self, code, asof):
        f = self._filed(code, asof, n=8)
        last = f.iloc[-1]
        px = self._hist(code, asof).iloc[-1]
        mcap = px["mcap"]

        def ratio(a, b):
            return a / b if b not in (0, None) and pd.notna(b) and pd.notna(a) else np.nan

        rows = {
            "latest_filed_period_end": last["period_end"].strftime("%Y-%m-%d"),
            "filing_date": last["filing_date"].strftime("%Y-%m-%d"),
            "sales_ttm_krw": last.get("sales_ttm"), "operating_income_ttm_krw": last.get("op_income_ttm"),
            "net_income_ttm_krw": last.get("net_income_ttm"), "operating_cash_flow_ttm_krw": last.get("cfo_ttm"),
            "ROE_ttm": last.get("ROE"), "ROA_ttm": last.get("ROA"), "operating_margin_ttm": last.get("OPM"),
            "gross_profit_to_assets": last.get("GPOA"), "debt_to_equity": last.get("DEBT_RATIO"),
            "quick_ratio": last.get("QUICK_RATIO"), "interest_coverage": last.get("ICR"),
            "sales_growth_yoy_latest_quarter": last.get("SALES_GROWTH"),
            "operating_income_growth_yoy_latest_quarter": last.get("OP_GROWTH"),
            "asset_growth_yoy": last.get("ASSET_GROWTH"),
            "market_cap_krw": mcap,
            "PER": ratio(mcap, last.get("net_income_ttm")), "PBR": ratio(mcap, last.get("equity")),
            "PCR": ratio(mcap, last.get("cfo_ttm")),
        }
        lines = [f"# Fundamentals for {code} ({self.name_of(code)}) using statements filed on or before {asof}",
                 "# Amounts in KRW. TTM = sum of the last four filed quarters. No analyst estimates are available."]
        for k, x in rows.items():
            if isinstance(x, str):
                lines.append(f"{k}: {x}")
            elif pd.isna(x):
                lines.append(f"{k}: n/a")
            elif k.endswith("_krw"):
                lines.append(f"{k}: {x:,.0f}")
            else:
                lines.append(f"{k}: {x:.3f}")
        return "\n".join(lines)

    _STATEMENT_COLS = {
        "income": ["sales", "gross_profit", "op_income", "net_income", "interest_expense"],
        "balance": ["equity", "assets", "liabilities", "current_assets", "current_liabilities", "inventory",
                    "cash", "debt"],
        "cashflow": ["cfo", "capex", "depreciation"],
    }

    def statement_text(self, code, kind, freq, asof):
        f = self._filed(code, asof, n=4)
        cols = [c for c in self._STATEMENT_COLS[kind] if c in f.columns]
        t = f[["period_end", "filing_date"] + cols].copy()
        t["period_end"] = t["period_end"].dt.strftime("%Y-%m-%d")
        t["filing_date"] = t["filing_date"].dt.strftime("%Y-%m-%d")
        note = "# Only stand-alone quarterly figures exist here" + (
            "; annual statements are not available." if str(freq).lower().startswith("a") else ".")
        return (f"# {kind} statement items for {code} ({self.name_of(code)}), last 4 quarters filed by {asof} (KRW)\n"
                f"{note}\n" + t.to_string(index=False, float_format=lambda x: f"{x:,.0f}"))

    # ------------------------------------------------------------------ macro
    def macro_text(self, indicator, asof, look_back_days=None):
        if self.macro is None:
            raise LookupError("macro.parquet not available")
        key = MACRO_ALIASES.get(str(indicator).strip().lower().replace(" ", "_"), str(indicator).strip().upper())
        if key not in MACRO_TITLES:
            return (f"NO_DATA_AVAILABLE: unknown macro indicator {indicator!r}. Available: "
                    + ", ".join(sorted(set(MACRO_ALIASES))) + ".")
        end = pd.Timestamp(asof)
        s = self.macro[(self.macro["name"] == key) & (self.macro["avail_date"] <= end)]
        if s.empty:
            raise LookupError(f"no observation of {key} public by {asof}")
        window = s[s["avail_date"] >= end - pd.Timedelta(days=int(look_back_days or 365))]
        window = window if len(window) else s.tail(1)
        title, unit = MACRO_TITLES[key]
        first, lastv = window["value"].iloc[0], window["value"].iloc[-1]
        tail = window.tail(12).copy()
        tail["avail_date"] = tail["avail_date"].dt.strftime("%Y-%m-%d")
        return (f"# {title} ({unit}), observations public on or before {asof}\n"
                f"latest: {lastv:,.4f} (public {window['avail_date'].iloc[-1]:%Y-%m-%d})\n"
                f"change over window: {lastv - first:+,.4f}\n"
                + tail[["avail_date", "value"]].to_string(index=False, float_format=lambda x: f"{x:,.4f}"))

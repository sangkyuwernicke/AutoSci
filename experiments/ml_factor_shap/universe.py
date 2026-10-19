"""Universe construction helpers: point-in-time eligibility, manual exclusions, statement-coverage filter.

Plan: KOSPI + KOSDAQ common stocks; exclude financials, SPACs and administrative / investment-caution issues.
"""
import numpy as np
import pandas as pd

# Keywords used when no sector is available (e.g. already delisted names). Conservative on purpose:
# a few non-financial firms with "금융" in the name get dropped, which is cheaper than keeping banks.
FIN_NAME_HINTS = ("금융지주", "은행", "증권", "보험", "생명", "화재", "캐피탈", "카드", "저축", "리츠", "투자회사")
SPAC_NAME_HINTS = ("스팩", "기업인수목적")
FIN_SECTOR_HINTS = ("금융", "은행", "보험", "증권")

BASE_STATEMENT_COLS = ["PER", "PBR", "PCR", "EV_EBITDA", "ROE", "ROA", "OPM", "GPOA",
                       "SALES_GROWTH", "OP_GROWTH", "DEBT_RATIO", "QUICK_RATIO", "ICR"]


def classify(ticker, name, sector=None, industry=None):
    """-> (is_financial, is_spac) from sector/industry text when present, else from the name."""
    name = str(name or "")
    spac = any(h in name for h in SPAC_NAME_HINTS)
    text = " ".join(str(x) for x in (sector, industry) if isinstance(x, str) and x)
    fin = any(h in text for h in FIN_SECTOR_HINTS) if text else any(h in name for h in FIN_NAME_HINTS)
    return fin, spac


def build_eligibility(members, names, sectors=None, industries=None):
    """members: DataFrame[month, ticker, market] = tickers listed on that month-end (point in time,
    includes names delisted later). Returns the same frame plus bool `eligible`."""
    sectors, industries = sectors or {}, industries or {}
    flags = {t: classify(t, names.get(t), sectors.get(t), industries.get(t)) for t in members["ticker"].unique()}
    m = members.copy()
    m["eligible"] = [not (flags[t][0] or flags[t][1]) for t in m["ticker"]]
    return m


def apply_exclusions(panel, exclusions):
    """exclusions: DataFrame[ticker, start, end] (e.g. administrative issues, caution designations).
    Rows with start <= date <= end are removed."""
    if exclusions is None or exclusions.empty:
        return panel
    ex = exclusions.copy()
    ex["start"], ex["end"] = pd.to_datetime(ex["start"]), pd.to_datetime(ex["end"]).fillna(pd.Timestamp.max)
    drop = pd.Series(False, index=panel.index)
    for t, g in ex.groupby("ticker"):
        sel = panel["ticker"] == t
        for _, r in g.iterrows():
            drop |= sel & (panel["date"] >= r["start"]) & (panel["date"] <= r["end"])
    print(f"[universe] exclusions removed {int(drop.sum()):,} stock-months")
    return panel[~drop]


def coverage_filter(panel, min_coverage=0.5, cols=BASE_STATEMENT_COLS):
    """Drop stock-months where fewer than `min_coverage` of the statement-based factors exist
    (typically newly listed names with no filing yet) instead of letting them sit at the median."""
    cols = [c for c in cols if c in panel.columns]
    if not cols or min_coverage <= 0:
        return panel
    cov = panel[cols].replace([np.inf, -np.inf], np.nan).notna().mean(axis=1)
    keep = cov >= min_coverage
    print(f"[universe] coverage filter (>= {min_coverage:.0%} of {len(cols)} statement factors) "
          f"removed {int((~keep).sum()):,} of {len(panel):,} stock-months")
    return panel[keep]

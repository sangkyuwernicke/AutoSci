"""Collect raw KOSPI/KOSDAQ inputs for data_real.build_panel.   *** UNTESTED ***

Written against the public APIs but never run (it needs DART/ECOS keys and network access that were
not available when this was authored). Expect to fix column names / series codes on first run, and
spot-check a few tickers against the DART viewer before trusting any number.

    export DART_KEY=... ECOS_KEY=...
    python fetch_real_data.py prices   --out data/real
    python fetch_real_data.py macro    --out data/real
    python fetch_real_data.py fundamentals --out data/real
"""
import argparse
import os
from pathlib import Path

import pandas as pd
import requests

from config import ECOS_SERIES

START, END = "2012-01-01", "2025-12-31"   # 2 years of warm-up for 12M momentum / YoY growth


def fetch_prices(out):
    import FinanceDataReader as fdr
    from pykrx import stock
    listing = fdr.StockListing("KRX")                       # current listing; add delisted names yourself
    # Survivorship: this universe only holds names alive today. Merge a historical listing
    # (e.g. KRX data portal / pykrx per-year ticker lists) before drawing conclusions.
    frames = []
    for _, r in listing.iterrows():
        if r["Market"] not in ("KOSPI", "KOSDAQ"):
            continue
        d = fdr.DataReader(r["Code"], START, END)[["Close"]].rename(columns={"Close": "close"})
        d["ticker"], d["market"] = r["Code"], r["Market"]
        # eligibility: exclude financials / SPAC / administrative issues. FDR's Sector column covers
        # the first two statically; per-date administrative-issue flags must come from KRX.
        d["eligible"] = ("스팩" not in str(r["Name"])) and ("금융" not in str(r.get("Dept", "")))
        frames.append(d.reset_index().rename(columns={"Date": "date"}))
    px = pd.concat(frames)
    # historical market cap at each month-end from pykrx
    caps = []
    for d in pd.date_range(START, END, freq="ME"):
        day = stock.get_nearest_business_day_in_a_week(d.strftime("%Y%m%d"))
        c = stock.get_market_cap_by_ticker(day, market="ALL")[["시가총액"]].rename(columns={"시가총액": "mcap"})
        c["date"] = pd.Timestamp(day); c["ticker"] = c.index
        caps.append(c.reset_index(drop=True))
    caps = pd.concat(caps)
    px["month"] = px["date"] + pd.offsets.MonthEnd(0)
    caps["month"] = caps["date"] + pd.offsets.MonthEnd(0)
    px = px.merge(caps[["month", "ticker", "mcap"]], on=["month", "ticker"], how="left")
    px["mcap"] = px.groupby("ticker")["mcap"].ffill()
    px.drop(columns="month").to_parquet(out / "prices.parquet")


def ecos(stat, cycle, item, start, end):
    key = os.environ["ECOS_KEY"]
    fmt = (lambda s: s.replace("-", "")[:6]) if cycle == "M" else (lambda s: s.replace("-", ""))
    url = (f"https://ecos.bok.or.kr/api/StatisticSearch/{key}/json/kr/1/100000/"
           f"{stat}/{cycle}/{fmt(start)}/{fmt(end)}/{item}")
    rows = requests.get(url, timeout=60).json()["StatisticSearch"]["row"]
    df = pd.DataFrame(rows)
    df["ref"] = pd.to_datetime(df["TIME"], format="%Y%m" if cycle == "M" else "%Y%m%d")
    return df.set_index("ref")["DATA_VALUE"].astype(float)


def fetch_macro(out):
    s = {k: ecos(v["stat"], v["cycle"], v["item"], START, END) for k, v in ECOS_SERIES.items()}
    cpi = s["CPI_INDEX"]
    cpi_yoy = cpi.pct_change(12) * 100
    # CPI for month m is published in early month m+1: assume the 5th (verify against the KOSTAT calendar)
    cpi_avail = cpi_yoy.index + pd.offsets.MonthEnd(0) + pd.Timedelta(days=5)
    long = [pd.DataFrame(dict(name="CPI_YOY", avail_date=cpi_avail, value=cpi_yoy.values)).dropna()]
    # Base rate: monthly table value is the month-end level; it is public at the decision date itself.
    long.append(pd.DataFrame(dict(name="BASE_RATE", avail_date=s["BASE_RATE"].index + pd.offsets.MonthEnd(0),
                                  value=s["BASE_RATE"].values)))
    for name, ser in [("KRWUSD", s["KRWUSD"]), ("TERM_SPREAD", s["KTB10Y"] - s["KTB3Y"])]:
        long.append(pd.DataFrame(dict(name=name, avail_date=ser.index, value=ser.values)).dropna())
    # VKOSPI: not on ECOS. Supply it from KRX (data.krx.co.kr -> derivatives index) as columns
    # name="VKOSPI", avail_date, value, appended to macro.parquet.
    pd.concat(long).to_parquet(out / "macro.parquet")
    print("NOTE: VKOSPI must be appended manually; build_panel will drop all rows until it is present.")


# account_id -> field. Company-specific IDs are common in DART; unmapped fields stay NaN.
IS_MAP = {"ifrs-full_Revenue": "sales", "ifrs-full_GrossProfit": "gross_profit",
          "dart_OperatingIncomeLoss": "op_income",
          "ifrs-full_ProfitLossAttributableToOwnersOfParent": "net_income",
          "ifrs-full_FinanceCosts": "interest_expense",   # proxy: finance costs, not pure interest
          # R&D: no single standard tag. Only some firms show it on the face of the statement; the
          # rest disclose it in the notes / business report (use the name fallback below, else 0).
          "ifrs-full_ResearchAndDevelopmentExpense": "rd"}
CF_MAP = {"ifrs-full_CashFlowsFromUsedInOperatingActivities": "cfo",
          "ifrs-full_PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities": "capex"}
RD_NAME_HINTS = ("연구개발비", "경상연구개발", "경상개발비")   # account_nm fallback for "rd"
BS_MAP = {"ifrs-full_Equity": "equity", "ifrs-full_Assets": "assets", "ifrs-full_Liabilities": "liabilities",
          "ifrs-full_CurrentAssets": "current_assets", "ifrs-full_CurrentLiabilities": "current_liabilities",
          "ifrs-full_Inventories": "inventory", "ifrs-full_CashAndCashEquivalents": "cash",
          "ifrs-full_Borrowings": "debt"}                 # proxy: total borrowings
REPORTS = {"11013": 3, "11012": 6, "11014": 9, "11011": 12}   # reprt_code -> months covered


def _amt(x):
    return pd.to_numeric(str(x).replace(",", ""), errors="coerce")


def fetch_fundamentals(out, tickers=None):
    import OpenDartReader
    dart = OpenDartReader(os.environ["DART_KEY"])
    tickers = tickers or sorted(pd.read_parquet(out / "prices.parquet", columns=["ticker"])["ticker"].unique())
    rows = []
    for t in tickers:
        ytd = {}                                             # (year, months) -> dict of YTD flows, filing date
        for year in range(int(START[:4]) - 1, int(END[:4]) + 1):
            for code, months in REPORTS.items():
                try:
                    fs = dart.finstate_all(t, year, reprt_code=code, fs_div="CFS")
                except Exception:
                    fs = None
                if fs is None or len(fs) == 0:
                    continue
                # DART receipt numbers start with the filing date: YYYYMMDD + 6 digits
                filed = pd.to_datetime(str(fs["rcept_no"].iloc[0])[:8])
                rec = {"filing_date": filed}
                for _, a in fs.iterrows():
                    for mp in (IS_MAP, CF_MAP, BS_MAP):
                        hit = a["account_id"] in mp or (mp is IS_MAP and any(h in str(a["account_nm"]) for h in RD_NAME_HINTS))
                        if hit:
                            key = mp.get(a["account_id"], "rd")
                            # IS in the H1/Q3 reports: thstrm_amount is the 3-month figure, the
                            # cumulative one is thstrm_add_amount. Everything else is already YTD/point-in-time.
                            col = "thstrm_add_amount" if (mp is IS_MAP and months in (6, 9)) else "thstrm_amount"
                            rec.setdefault(key, _amt(a[col]))
                ytd[(year, months)] = rec
        for (year, months), rec in ytd.items():              # YTD -> stand-alone quarter
            prev = ytd.get((year, months - 3))
            row = {"ticker": t, "period_end": pd.Timestamp(year, months, 1) + pd.offsets.MonthEnd(0),
                   "filing_date": rec["filing_date"]}
            if months == 12:                                  # annual R&D intensity inputs (full-year figures)
                row["sales_annual"], row["rd_annual"] = rec.get("sales"), rec.get("rd")
            for k, v in rec.items():
                if k in ("filing_date", "rd"):                # rd is annual-only; not turned into quarters
                    continue
                row[k] = v - prev.get(k, 0) if (k in IS_MAP.values() or k in CF_MAP.values()) and prev else v
            rows.append(row)
    pd.DataFrame(rows).to_parquet(out / "fundamentals.parquet")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["prices", "macro", "fundamentals"])
    ap.add_argument("--out", default="data/real")
    a = ap.parse_args()
    o = Path(a.out); o.mkdir(parents=True, exist_ok=True)
    {"prices": fetch_prices, "macro": fetch_macro, "fundamentals": fetch_fundamentals}[a.what](o)

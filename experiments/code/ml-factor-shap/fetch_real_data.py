"""Collect macro and fundamentals inputs for data_real.build_panel.   *** UNTESTED against the live APIs ***

KRX prices/universe are NOT fetched here: KRX forbids automated collection (our pykrx route got an IP blocked).
Download the KRX screens by hand and convert them with prepare_krx.py.

Written against the public APIs but never run (it needs DART/ECOS keys and network access that were not available
when this was authored). Expect to fix column names / series codes on first run, and spot-check a few tickers
against the DART viewer before trusting any number.

    put DART_KEY=... and ECOS_KEY=... in the repo-root .env (git-ignored) or ~/.env, or export them
    python prepare_krx.py --krx-dir data/krx --out data/real              # first: gives prices_monthly.parquet
    python fetch_real_data.py macro --out data/real --start-year 2019      # needs data/krx/vkospi.csv for VKOSPI
    python fetch_real_data.py fundamentals --out data/real --market KOSPI --top-n-mcap 100 --start-year 2019
"""
import argparse
import os
from pathlib import Path

import pandas as pd
import requests

from config import ECOS_SERIES



def _load_env():
    """Read KEY=VALUE lines from ~/.env and the repo-root .env (found by walking up from this file).
    Variables already set in the environment are never overwritten."""
    here = Path(__file__).resolve()
    for f in [Path.home() / ".env"] + [d / ".env" for d in here.parents]:
        if not f.is_file():
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip("\"'"))


_load_env()
START, END = "2012-01-01", "2025-12-31"   # 2 years of warm-up for 12M momentum / YoY growth


def ecos(stat, cycle, item, start, end):
    key = os.environ["ECOS_KEY"]
    fmt = (lambda s: s.replace("-", "")[:6]) if cycle == "M" else (lambda s: s.replace("-", ""))
    url = (f"https://ecos.bok.or.kr/api/StatisticSearch/{key}/json/kr/1/100000/"
           f"{stat}/{cycle}/{fmt(start)}/{fmt(end)}/{item}")
    rows = requests.get(url, timeout=60).json()["StatisticSearch"]["row"]
    df = pd.DataFrame(rows)
    df["ref"] = pd.to_datetime(df["TIME"], format="%Y%m" if cycle == "M" else "%Y%m%d")
    return df.set_index("ref")["DATA_VALUE"].astype(float)


def fetch_macro(out, krx_dir="data/krx"):
    s = {k: ecos(v["stat"], v["cycle"], v["item"], START, END) for k, v in ECOS_SERIES.items()}
    cpi = s["CPI_INDEX"]
    cpi_yoy = cpi.pct_change(12) * 100
    # CPI for month m is published in early month m+1: assume the 5th (verify against the KOSTAT calendar)
    cpi_avail = cpi_yoy.index + pd.offsets.MonthEnd(0) + pd.DateOffset(days=5)
    long = [pd.DataFrame(dict(name="CPI_YOY", avail_date=cpi_avail, value=cpi_yoy.values)).dropna()]
    # Base rate: monthly table value is the month-end level; it is public at the decision date itself.
    long.append(pd.DataFrame(dict(name="BASE_RATE", avail_date=s["BASE_RATE"].index + pd.offsets.MonthEnd(0),
                                  value=s["BASE_RATE"].values)))
    for name, ser in [("KRWUSD", s["KRWUSD"]), ("TERM_SPREAD", s["KTB10Y"] - s["KTB3Y"])]:
        long.append(pd.DataFrame(dict(name=name, avail_date=ser.index, value=ser.values)).dropna())
    # VKOSPI is not on ECOS: hand-download it from KRX (index screen) to <krx_dir>/vkospi.csv (일자,종가)
    macro = pd.concat(long)
    macro.to_parquet(out / "macro.parquet")
    from prepare_krx import append_vkospi
    append_vkospi(out, krx_dir)


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


def _dart_client():
    """OpenDartReader moved from `import OpenDartReader` (old releases) to `from opendartreader import
    OpenDartReader` (>= 0.3). Accept both. The client downloads the corp-code list into ./docs_cache."""
    try:
        from opendartreader import OpenDartReader
    except ImportError:
        try:
            import OpenDartReader
        except ImportError:
            raise SystemExit("pip install opendartreader   (requirements.txt lists it)")
    return OpenDartReader(os.environ["DART_KEY"])


def _fetch_one(dart, t, years):
    """All filings of one ticker -> stand-alone quarterly rows (see module docstring for the schema)."""
    ytd = {}                                                 # (year, months) -> dict of YTD flows, filing date
    for year in years:
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
    rows = []
    for (year, months), rec in ytd.items():                  # YTD -> stand-alone quarter
        prev = ytd.get((year, months - 3))
        row = {"ticker": t, "period_end": pd.Timestamp(year, months, 1) + pd.offsets.MonthEnd(0),
               "filing_date": rec["filing_date"]}
        if months == 12:                                      # annual R&D intensity inputs (full-year figures)
            row["sales_annual"], row["rd_annual"] = rec.get("sales"), rec.get("rd")
        for k, v in rec.items():
            if k in ("filing_date", "rd"):                    # rd is annual-only; not turned into quarters
                continue
            row[k] = v - prev.get(k, 0) if (k in IS_MAP.values() or k in CF_MAP.values()) and prev else v
        rows.append(row)
    return pd.DataFrame(rows)


def select_tickers(out, market=None, top_n_mcap=0):
    """Tickers to fetch: eligible names in prices_monthly.parquet (from prepare_krx.py), optionally one market and
    the N largest by latest market cap. Keep this small: every ticker costs years x 4 DART calls."""
    pm = pd.read_parquet(out / "prices_monthly.parquet")
    pm = pm[pm["eligible"]]
    if market:
        pm = pm[pm["market"] == market]
    if top_n_mcap:
        # largest by market cap in the most recent snapshot, else by each name's last known value
        lastcap = pm.sort_values("date").groupby("ticker")["mcap"].last()
        return sorted(lastcap.nlargest(top_n_mcap).index)
    return sorted(pm["ticker"].unique())


def fetch_fundamentals(out, tickers=None, start_year=None, max_calls=6000):
    """Resumable: one parquet per ticker in <out>/dart_cache, so a rerun only asks DART for missing tickers.
    DART is an official API with a daily call quota; the planned call count is checked against `max_calls`."""
    first = start_year or int(START[:4]) - 1
    years = list(range(first, int(END[:4]) + 1))
    if tickers is None:
        tickers = select_tickers(out)
    cache = out / "dart_cache"; cache.mkdir(exist_ok=True)
    todo = [t for t in tickers if not (cache / f"{t}.parquet").exists()]
    planned = len(todo) * len(years) * len(REPORTS)
    print(f"[dart] {len(tickers)} tickers ({len(tickers) - len(todo)} cached), years {years[0]}-{years[-1]}: "
          f"{planned:,} calls planned (limit {max_calls:,})")
    if planned > max_calls:
        raise SystemExit("planned DART calls exceed --max-calls; narrow with --market/--top-n-mcap/--start-year "
                         "or raise --max-calls knowingly (check your key's daily quota first).")
    dart = _dart_client() if todo else None
    for i, t in enumerate(todo, 1):
        _fetch_one(dart, t, years).to_parquet(cache / f"{t}.parquet")
        if i % 10 == 0:
            print(f"[dart] {i}/{len(todo)} tickers")
    frames = [pd.read_parquet(cache / f"{t}.parquet") for t in tickers]
    df = pd.concat([f for f in frames if len(f)], ignore_index=True)
    print(f"[dart] {len(df):,} quarterly rows, {df['ticker'].nunique()} tickers with filings; "
          f"R&D found for {df['rd_annual'].notna().groupby(df['ticker']).any().sum() if 'rd_annual' in df else 0}")
    df.to_parquet(out / "fundamentals.parquet")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["macro", "fundamentals"],
                    help="prices are no longer fetched: use prepare_krx.py on hand-downloaded KRX files")
    ap.add_argument("--out", default="data/real")
    ap.add_argument("--krx-dir", default="data/krx", help="macro: where vkospi.csv lives")
    ap.add_argument("--start-year", type=int, default=None,
                    help="first fiscal year to fetch (default: 2011, i.e. one year before START)")
    ap.add_argument("--end-year", type=int, default=None)
    ap.add_argument("--market", choices=["KOSPI", "KOSDAQ"], default=None, help="fundamentals: restrict tickers")
    ap.add_argument("--top-n-mcap", type=int, default=0, help="fundamentals: only the N largest tickers")
    ap.add_argument("--max-calls", type=int, default=6000, help="fundamentals: refuse to start above this many calls")
    a = ap.parse_args()
    o = Path(a.out); o.mkdir(parents=True, exist_ok=True)
    if a.start_year:
        START = f"{a.start_year - (0 if a.what == 'fundamentals' else 1)}-01-01"
    if a.end_year:
        END = f"{a.end_year}-12-31"
    if a.what == "macro":
        fetch_macro(o, a.krx_dir)
    else:
        fetch_fundamentals(o, select_tickers(o, a.market, a.top_n_mcap), a.start_year, a.max_calls)

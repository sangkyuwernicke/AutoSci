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
import pickle
import re
import time
from pathlib import Path

import numpy as np
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


class DartStop(Exception):
    """Stop the whole run (quota hit, daily budget used up, or DART unavailable). Nothing partial is cached as final."""


class _Budget:
    """Call counter + minimum spacing between requests (stay well below DART's per-minute limit)."""
    limit = None            # max HTTP calls in this run (None = unlimited)
    min_interval = 0.12     # seconds between calls (~500/min)
    used = 0
    _last = 0.0

    @classmethod
    def tick(cls):
        if cls.limit is not None and cls.used >= cls.limit:
            raise DartStop(f"daily call budget reached ({cls.used:,} calls). Rerun later; cached tickers and "
                           "finished years are skipped.")
        wait = cls.min_interval - (time.monotonic() - cls._last)
        if wait > 0:
            time.sleep(wait)
        cls._last = time.monotonic()
        cls.used += 1


DART_URL = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"
QUOTA_STATUS = {"020"}                  # request limit exceeded
RETRY_STATUS = {"800", "900"}           # service maintenance / unknown error: retry, then stop
MAX_RETRIES = 3


def _finstate(dart, ticker, year, code, fs_div="CFS"):
    """One DART call with explicit status handling. Returns a DataFrame, or None when DART says there is no data
    (status 013 = a legitimate gap). Quota or persistent errors raise DartStop, so a failure can never be mistaken
    for 'no filing' and cached as empty."""
    corp = dart.find_corp_code(ticker)
    if not corp:
        return None
    for attempt in range(1, MAX_RETRIES + 1):
        _Budget.tick()
        try:
            r = requests.get(DART_URL, params={"crtfc_key": os.environ["DART_KEY"], "corp_code": corp,
                                               "bsns_year": year, "reprt_code": code, "fs_div": fs_div}, timeout=30)
            r.raise_for_status()
            jo = r.json()
        except (requests.RequestException, ValueError) as e:
            err = f"{type(e).__name__}: {e}"
        else:
            status = str(jo.get("status", ""))
            if status == "000" and "list" in jo:
                df = pd.DataFrame(jo["list"])
                if "account_id" in df.columns:               # filings before the 2019 taxonomy use `ifrs_X`
                    df["account_id"] = df["account_id"].astype(str).str.replace(r"^ifrs_", "ifrs-full_", regex=True)
                return df
            if status == "013":
                return None
            if status in QUOTA_STATUS:
                raise DartStop(f"DART quota exceeded (status {status}: {jo.get('message')}) after "
                               f"{_Budget.used:,} calls this run. Wait for the daily reset and rerun.")
            err = f"status {status}: {jo.get('message')}"
            if status not in RETRY_STATUS:
                raise DartStop(f"unexpected DART response for {ticker} {year} {code}: {err}")
        time.sleep(2 ** attempt)
    raise DartStop(f"DART failed {MAX_RETRIES} times for {ticker} {year} {code} ({err})")


# Fallbacks for fields the standard-tag maps miss (most Korean filers use split or company-specific tags).
_DEBT_NAME = re.compile(r"^(유동성)?(단기|장기)?(차입금|차입부채|사채|발행사채|사채및차입금|차입금및사채|전자단기사채|단기사채)$")
_SALES_NAMES = ("매출액", "영업수익", "수익(매출액)", "매출")


def _fallbacks(fs, rec, months):
    """debt = sum of distinct borrowing / bond lines on the balance sheet (the old single-tag
    `ifrs-full_Borrowings` hit <1 % of filings); net_income falls back to ProfitLoss on IS/CIS;
    sales falls back to account names."""
    if "sj_div" not in fs.columns:                          # enrichment only; never break the main parse
        return
    nm = fs["account_nm"].astype(str).str.replace(r"\s+", "", regex=True)
    bs = fs[(fs["sj_div"] == "BS") & nm.str.match(_DEBT_NAME)]
    if len(bs):
        vals = bs.assign(nm=nm[bs.index]).drop_duplicates("nm")["thstrm_amount"].map(_amt)
        rec["debt"] = float(vals.sum(skipna=True))
    is_ = fs[fs["sj_div"].isin(["IS", "CIS"])]
    col = "thstrm_add_amount" if months in (6, 9) else "thstrm_amount"
    if pd.isna(rec.get("net_income", np.nan)):
        for aid in ("ifrs-full_ProfitLossAttributableToOwnersOfParent", "ifrs-full_ProfitLoss"):
            h = is_[is_["account_id"] == aid]
            if len(h):
                rec["net_income"] = _amt(h[col].iloc[0])
                break
    if pd.isna(rec.get("sales", np.nan)):
        h = is_[is_["account_nm"].astype(str).str.replace(r"\s+", "", regex=True).isin(_SALES_NAMES)]
        if len(h):
            rec["sales"] = _amt(h[col].iloc[0])


def _fetch_one(dart, t, years, partial_dir=None):
    """All filings of one ticker -> stand-alone quarterly rows (see module docstring for the schema).
    Finished years are checkpointed in <partial_dir>/<ticker>.pkl, so a run stopped by DartStop resumes at the
    first unfinished year instead of repeating the whole ticker."""
    ytd, done = {}, set()                                    # ytd: (year, months) -> YTD flows + filing date
    ck = (Path(partial_dir) / f"{t}.pkl") if partial_dir else None
    if ck is not None and ck.exists():
        ytd, done = pickle.loads(ck.read_bytes())
    for year in years:
        if year in done:
            continue
        for code, months in REPORTS.items():
            fs = _finstate(dart, t, year, code)
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
            _fallbacks(fs, rec, months)
            ytd[(year, months)] = rec
        done.add(year)
        if ck is not None:
            ck.write_bytes(pickle.dumps((ytd, done)))
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


def select_tickers(out, market=None, top_n_mcap=0, since="2015-01-01"):
    """Tickers to fetch: eligible names that traded on/after `since` (prices.parquet from prepare_marcap.py, else
    prices_monthly.parquet), optionally one market and the N largest by latest market cap. Every ticker costs
    years x 4 DART calls, so keep the universe and the year range tight."""
    f = out / "prices.parquet"
    pm = pd.read_parquet(f, columns=["date", "ticker", "market", "eligible", "mcap"]) if f.exists() \
        else pd.read_parquet(out / "prices_monthly.parquet")
    pm = pm[pm["eligible"] & (pd.to_datetime(pm["date"]) >= pd.Timestamp(since))]
    if market:
        pm = pm[pm["market"] == market]
    if top_n_mcap:
        lastcap = pm.sort_values("date").groupby("ticker")["mcap"].last()
        return sorted(lastcap.nlargest(top_n_mcap).index)
    return sorted(pm["ticker"].unique())


def fetch_fundamentals(out, tickers=None, start_year=None, max_calls=6000, daily_budget=None,
                       cache_name="dart_cache", base_cache=None, base_from_year=None,
                       base_table=None, base_before_year=None):
    """Resumable: one parquet per ticker in <out>/dart_cache, so a rerun only asks DART for missing tickers.
    DART is an official API with a daily call quota; the planned call count is checked against `max_calls`.
    Repair mode: fetch only an early year range into `cache_name` and, when the final table is built, append the rows of
    `base_cache` whose period_end year is >= `base_from_year` (quarters convert YTD -> stand-alone inside one year, so
    years are independent and the good years of an older cache stay valid)."""
    first = start_year or int(START[:4]) - 1
    years = list(range(first, int(END[:4]) + 1))
    if tickers is None:
        tickers = select_tickers(out)
    cache = out / cache_name; cache.mkdir(exist_ok=True)
    todo = [t for t in tickers if not (cache / f"{t}.parquet").exists()]
    planned = len(todo) * len(years) * len(REPORTS)
    print(f"[dart] {len(tickers)} tickers ({len(tickers) - len(todo)} cached), years {years[0]}-{years[-1]}: "
          f"{planned:,} calls planned (limit {max_calls:,})")
    if planned > max_calls:
        raise SystemExit("planned DART calls exceed --max-calls; narrow with --market/--top-n-mcap/--start-year "
                         "or raise --max-calls knowingly (check your key's daily quota first).")
    dart = _dart_client() if todo else None
    partial = cache / "_partial"; partial.mkdir(exist_ok=True)
    _Budget.limit = daily_budget
    try:
        for i, t in enumerate(todo, 1):
            _fetch_one(dart, t, years, partial).to_parquet(cache / f"{t}.parquet")
            (partial / f"{t}.pkl").unlink(missing_ok=True)
            if i % 10 == 0:
                print(f"[dart] {i}/{len(todo)} tickers, {_Budget.used:,} calls this run")
    except DartStop as e:
        left = sum(1 for t in tickers if not (cache / f"{t}.parquet").exists())
        print(f"\n[dart] STOPPED: {e}\n[dart] {len(tickers) - left}/{len(tickers)} tickers cached, {left} left. "
              f"fundamentals.parquet was NOT rewritten; rerun the same command to continue.")
        raise SystemExit(2)
    frames = [pd.read_parquet(cache / f"{t}.parquet") for t in tickers]
    if base_cache:
        for t in tickers:
            b = out / base_cache / f"{t}.parquet"
            if b.exists():
                b = pd.read_parquet(b)
                if len(b):                                   # tickers without filings are cached as empty frames
                    frames.append(b[b["period_end"].dt.year >= base_from_year])
    if base_table:                                           # extend: keep the finished table's earlier fiscal years
        bt = pd.read_parquet(base_table)
        frames.append(bt[bt["period_end"].dt.year < base_before_year])
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
    ap.add_argument("--cache-name", default="dart_cache", help="fundamentals: cache directory under --out")
    ap.add_argument("--base-cache", default=None,
                    help="fundamentals: also use this older cache for fiscal years >= --base-from-year")
    ap.add_argument("--base-from-year", type=int, default=None)
    ap.add_argument("--base-table", default=None,
                    help="fundamentals: finished fundamentals.parquet whose rows with period_end year < "
                         "--base-before-year are kept (extend a table to new years)")
    ap.add_argument("--base-before-year", type=int, default=None)
    ap.add_argument("--daily-budget", type=int, default=None,
                    help="fundamentals: stop cleanly after this many HTTP calls in this run (set below your DART "
                         "daily quota, e.g. 18000); rerun the next day to continue from the cache")
    a = ap.parse_args()
    o = Path(a.out); o.mkdir(parents=True, exist_ok=True)
    if a.start_year:
        START = f"{a.start_year - (0 if a.what == 'fundamentals' else 1)}-01-01"
    if a.end_year:
        END = f"{a.end_year}-12-31"
    if a.what == "macro":
        fetch_macro(o, a.krx_dir)
    else:
        fetch_fundamentals(o, select_tickers(o, a.market, a.top_n_mcap), a.start_year, a.max_calls,
                           a.daily_budget, a.cache_name, a.base_cache, a.base_from_year,
                           a.base_table, a.base_before_year)

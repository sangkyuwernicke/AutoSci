"""
KOSPI Top 10 data pipeline (v2)
Test window: 2026-07-01 ~ 2026-09-30
Data: daily prices + news (per-stock + market) + macro

Changes vs v1:
- Universe is chosen by market cap on the day BEFORE the test window
  (2026-06-30) instead of a hard-coded list (v1 had wrong/duplicate codes:
  Naver was given Kakao's code, Kakao appeared twice).
- News parsing handles Naver's "YYYY.MM.DD HH:MM" timestamps (v1 silently
  dropped every article) and paginates back until the window start.
- Market news is collected per date (v1 stamped today's headlines with now()).
- Every news row gets `usable_from`: the first trading session the agent is
  allowed to see it in (after 15:30 KST -> next session). Prevents lookahead.

NOT YET RUN. KRX/Naver/ECOS are not reachable from the cloud workspace, so
run this on your own machine. Start with `--dry-run` to check the HTML
selectors before the full crawl.

Usage:
    pip install -r requirements.txt
    export ECOS_API_KEY=...        # optional, for base rate / KTB yields
    python kospi_data_pipeline.py --dry-run
    python kospi_data_pipeline.py
"""

import argparse
import os
import time
from datetime import datetime, time as dtime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

TEST_START = "2026-07-01"
TEST_END = "2026-09-30"
UNIVERSE_DATE = "20260630"      # market-cap snapshot date (day before test)
TOP_N = 10
EXCLUDE_PREFERRED = True        # drop preferred shares like 005935
MARKET_CLOSE = dtime(15, 30)
SLEEP = 0.7                     # seconds between Naver requests
OUT = Path("kospi_data")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://finance.naver.com/",
}


# ---------------------------------------------------------------- universe
def build_universe() -> pd.DataFrame:
    """pykrx now needs a KRX login (KRX_ID / KRX_PW). Without it, fall back to Naver."""
    if not (os.environ.get("KRX_ID") and os.environ.get("KRX_PW")):
        print("  KRX_ID/KRX_PW not set -> using Naver market-cap ranking instead of pykrx")
        return build_universe_naver()
    from pykrx import stock
    cap = stock.get_market_cap(UNIVERSE_DATE, market="KOSPI")
    cap = cap.sort_values("시가총액", ascending=False)
    if EXCLUDE_PREFERRED:
        # KRX preferred shares end in 5/7/9/K etc.; common shares end in 0
        cap = cap[cap.index.str[-1] == "0"]
    top = cap.head(TOP_N).copy()
    top["name"] = [stock.get_market_ticker_name(t) for t in top.index]
    top = top.reset_index().rename(columns={"티커": "ticker", "시가총액": "market_cap"})
    return top[["ticker", "name", "market_cap"]]


def build_universe_naver(candidates: int = 30) -> pd.DataFrame:
    """
    1. Take today's top `candidates` KOSPI stocks by market cap from Naver.
    2. Shares outstanding = today's market cap / today's price.
    3. Market cap on UNIVERSE_DATE = that day's close x shares, re-rank, keep TOP_N.
    Approximation: uses today's share count (buybacks/issuance since June are ignored),
    and a stock that was top-10 in June but has since dropped out of the top 30 would be missed.
    """
    import re
    import FinanceDataReader as fdr
    rows = []
    url = "https://finance.naver.com/sise/sise_market_sum.naver?sosok=0&page=1"
    html = requests.get(url, headers=HEADERS, timeout=10)
    html.encoding = "euc-kr"
    soup = BeautifulSoup(html.text, "lxml")
    for tr in soup.select("table.type_2 tbody tr"):
        a = tr.select_one("a.tltle")
        tds = tr.select("td.number")
        if not a or len(tds) < 5:
            continue
        code = re.search(r"code=(\d{6})", a["href"]).group(1)
        price = float(tds[0].get_text(strip=True).replace(",", ""))
        cap_eok = float(tds[4].get_text(strip=True).replace(",", ""))   # 시가총액, 억원
        rows.append({"ticker": code, "name": a.get_text(strip=True),
                     "shares": cap_eok * 1e8 / price})
        if len(rows) >= candidates:
            break
    if not rows:
        raise RuntimeError("Naver market-cap page parsed 0 rows; selectors need updating")
    df = pd.DataFrame(rows)
    if EXCLUDE_PREFERRED:
        df = df[df.ticker.str[-1] == "0"]
    snap = pd.Timestamp(UNIVERSE_DATE)
    closes = []
    for t in df.ticker:
        px = fdr.DataReader(t, snap - pd.Timedelta(days=10), snap)["Close"]
        closes.append(px.iloc[-1] if len(px) else float("nan"))
        time.sleep(SLEEP)
    df["market_cap"] = df["shares"] * pd.Series(closes, index=df.index)
    return df.sort_values("market_cap", ascending=False).head(TOP_N)[["ticker", "name", "market_cap"]]


# ---------------------------------------------------------------- prices
def fetch_prices(universe: pd.DataFrame) -> pd.DataFrame:
    import FinanceDataReader as fdr
    frames = []
    for t, n in zip(universe.ticker, universe.name):
        df = fdr.DataReader(t, TEST_START, TEST_END)
        df = df.reset_index().rename(columns={"index": "Date"})
        df["ticker"], df["name"] = t, n
        frames.append(df)
        print(f"  price {n} ({t}): {len(df)} sessions")
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------- news
def _parse_ts(s: str):
    s = s.strip()
    for fmt in ("%Y.%m.%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y.%m.%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def fetch_stock_news(ticker: str, max_pages: int = 400, dry_run=False) -> list:
    start = datetime.fromisoformat(TEST_START)
    end = datetime.fromisoformat(TEST_END).replace(hour=23, minute=59)
    rows = []
    for page in range(1, max_pages + 1):
        url = f"https://finance.naver.com/item/news_news.naver?code={ticker}&page={page}"
        soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=10).text, "lxml")
        items = soup.select("table.type5 tr")
        page_ts = []
        for tr in items:
            a, d = tr.select_one("td.title a"), tr.select_one("td.date")
            if not a or not d:
                continue
            ts = _parse_ts(d.get_text())
            if ts is None:
                continue
            page_ts.append(ts)
            if start <= ts <= end:
                src = tr.select_one("td.info")
                rows.append({"timestamp": ts, "ticker": ticker, "scope": "stock",
                             "title": a.get_text(strip=True),
                             "source": src.get_text(strip=True) if src else "",
                             "url": "https://finance.naver.com" + a.get("href", "")})
        if dry_run:
            print(f"    dry-run page1: {len(page_ts)} rows parsed, "
                  f"newest={max(page_ts) if page_ts else None}")
            break
        if not page_ts or min(page_ts) < start:   # walked past window start
            break
        time.sleep(SLEEP)
    return rows


def fetch_market_news(dry_run=False) -> list:
    rows = []
    for day in pd.bdate_range(TEST_START, TEST_END):
        for page in range(1, 6):
            url = (f"https://finance.naver.com/news/mainnews.naver"
                   f"?date={day:%Y-%m-%d}&page={page}")
            soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=10).text, "lxml")
            items = soup.select("ul.newsList li")
            if not items:
                break
            for li in items:
                a = li.select_one("dd.articleSubject a") or li.select_one("dt.articleSubject a")
                w = li.select_one("span.wdate")
                if not a:
                    continue
                ts = _parse_ts(w.get_text()) if w else None
                rows.append({"timestamp": ts or day.to_pydatetime(), "ticker": None,
                             "scope": "market", "title": a.get_text(strip=True),
                             "source": "", "url": a.get("href", "")})
            time.sleep(SLEEP)
            if dry_run:
                print(f"    dry-run {day:%Y-%m-%d}: {len(items)} items")
                return rows
    return rows


def add_usable_from(news: pd.DataFrame, sessions: pd.DatetimeIndex) -> pd.DataFrame:
    """First trading session whose decision may use this article."""
    sess = pd.Series(sessions.normalize().unique()).sort_values().reset_index(drop=True)

    def usable(ts):
        d = pd.Timestamp(ts.date())
        if ts.time() >= MARKET_CLOSE:          # published after close
            later = sess[sess > d]
        else:
            later = sess[sess >= d]
        return later.iloc[0] if len(later) else pd.NaT

    news["usable_from"] = news["timestamp"].apply(usable)
    return news


# ---------------------------------------------------------------- macro
ECOS_SERIES = {   # (stat_code, cycle, item_code) -- verify codes on ECOS before relying on them
    "base_rate": ("722Y001", "D", "0101000"),
    "ktb_3y":    ("817Y002", "D", "010200000"),
}


def fetch_macro() -> pd.DataFrame:
    import FinanceDataReader as fdr
    out = pd.DataFrame()
    for col, sym in {"usdkrw": "USD/KRW", "kospi": "KS11", "sp500": "US500"}.items():
        s = fdr.DataReader(sym, TEST_START, TEST_END)["Close"].rename(col)
        out = out.join(s, how="outer") if len(out) else s.to_frame()
    key = os.environ.get("ECOS_API_KEY")
    if not key:
        print("  ECOS_API_KEY not set: skipping base rate / KTB yields")
        return out
    s, e = TEST_START.replace("-", ""), TEST_END.replace("-", "")
    for col, (code, cyc, item) in ECOS_SERIES.items():
        url = (f"https://ecos.bok.or.kr/api/StatisticSearch/{key}/json/kr/1/1000/"
               f"{code}/{cyc}/{s}/{e}/{item}")
        data = requests.get(url, timeout=15).json()
        rows = data.get("StatisticSearch", {}).get("row", [])
        ser = pd.Series({pd.to_datetime(r["TIME"]): float(r["DATA_VALUE"]) for r in rows}, name=col)
        print(f"  ECOS {col}: {len(ser)} obs")
        out = out.join(ser, how="outer")
    return out


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="one page per source, to check the HTML selectors")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)

    print("[1] universe (market cap on", UNIVERSE_DATE, ")")
    uni = build_universe()
    print(uni.to_string(index=False))
    uni.to_csv(OUT / "universe.csv", index=False)

    print("[2] prices")
    prices = fetch_prices(uni)
    prices.to_csv(OUT / "prices.csv", index=False)
    sessions = pd.DatetimeIndex(pd.to_datetime(prices["Date"]).unique())

    print("[3] news")
    rows = []
    for t, n in zip(uni.ticker, uni.name):
        r = fetch_stock_news(t, dry_run=args.dry_run)
        print(f"  {n}: {len(r)} articles in window")
        rows += r
    rows += fetch_market_news(dry_run=args.dry_run)
    news = pd.DataFrame(rows)
    if len(news):
        news["timestamp"] = pd.to_datetime(news["timestamp"])
        news = add_usable_from(news, sessions).drop_duplicates(["title", "ticker"])
    news.to_csv(OUT / "news.csv", index=False)

    print("[4] macro")
    macro = fetch_macro()
    macro.to_csv(OUT / "macro.csv")

    print(f"\nprices {len(prices)} rows | news {len(news)} rows | macro {len(macro)} rows -> {OUT}/")
    if len(news) == 0:
        print("WARNING: no news parsed - Naver HTML selectors probably changed.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""네이버 뉴스 수집 (네이버 검색 오픈 API) → JSONL/CSV 저장.

사전 준비: https://developers.naver.com 에서 애플리케이션 등록(검색 API) 후 .env 에
  NAVER_CLIENT_ID=...
  NAVER_CLIENT_SECRET=...

사용 예:
  python tools/fetch_news_naver.py --keyword 삼성전자 --max 200
  python tools/fetch_news_naver.py --keyword 삼성전자 --start 2026-10-01 --end 2026-10-31 --fulltext

주의:
- 검색 API는 start 최대 1000, display 최대 100(키워드당 최대 1,000건)이며 날짜 필터가 없어
  --start/--end 는 결과의 pubDate 로 클라이언트 측에서 거릅니다. 최신순(sort=date) 기본.
- --fulltext 는 n.news.naver.com 기사 페이지에서 본문(#dic_area)을 파싱합니다. 비공식이며
  네이버/언론사 약관·저작권을 준수하고 --delay 를 유지하세요. 네이버 외 링크는 요약문 유지.
- 출력 스키마는 fetch_news_bigkinds.py 와 동일하여 analyze_news_sentiment.py 에 그대로 입력 가능.
"""
from __future__ import annotations

import argparse
import html
import os
import re
import sys
import time
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests

import _env  # noqa: F401 — .env 의 API 키 로드
from fetch_news_bigkinds import save  # 동일 저장 포맷 재사용

API = "https://openapi.naver.com/v1/search/news.json"
TAG_RE = re.compile(r"<[^>]+>")
BODY_RE = re.compile(r'<article[^>]*id="dic_area"[^>]*>(.*?)</article>', re.S)


def clean(t: str | None) -> str:
    return re.sub(r"\s+", " ", html.unescape(TAG_RE.sub("", t or ""))).strip()


def search(keyword, max_items, sort="date", delay=0.2):
    cid, sec = os.environ.get("NAVER_CLIENT_ID"), os.environ.get("NAVER_CLIENT_SECRET")
    if not cid or not sec:
        raise SystemExit("NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 이 설정되지 않았습니다 (.env 확인).")
    h = {"X-Naver-Client-Id": cid, "X-Naver-Client-Secret": sec}
    items, start = [], 1
    while len(items) < max_items and start <= 1000:
        size = min(100, max_items - len(items))
        r = requests.get(API, headers=h, timeout=30,
                         params={"query": keyword, "display": size, "start": start, "sort": sort})
        r.raise_for_status()
        rows = r.json().get("items") or []
        if not rows:
            break
        for x in rows:
            try:
                d = parsedate_to_datetime(x["pubDate"]).strftime("%Y-%m-%d")
            except Exception:
                d = ""
            link = x.get("link") or ""
            items.append({
                "id": re.sub(r"\W+", "_", link.split("//")[-1])[:80], "date": d,
                "provider": "", "byline": "", "title": clean(x.get("title")),
                "content": clean(x.get("description")),  # 요약문
                "url": link, "originallink": x.get("originallink", ""), "keyword": keyword,
            })
        start += len(rows)
        time.sleep(delay)
    return items


def fetch_fulltext(session, url: str) -> str:
    if "news.naver.com" not in url:
        return ""
    r = session.get(url, timeout=30)
    r.raise_for_status()
    m = BODY_RE.search(r.text)
    return clean(m.group(1)) if m else ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--keyword", required=True)
    ap.add_argument("--max", type=int, default=100)
    ap.add_argument("--start", help="YYYY-MM-DD (pubDate 기준 필터)")
    ap.add_argument("--end", help="YYYY-MM-DD")
    ap.add_argument("--sort", choices=["date", "sim"], default="date")
    ap.add_argument("--fulltext", action="store_true")
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--out-dir", default="raw/tmp/news")
    a = ap.parse_args()

    items = search(a.keyword, a.max, a.sort)
    if a.start:
        items = [i for i in items if i["date"] >= a.start]
    if a.end:
        items = [i for i in items if i["date"] <= a.end]
    if a.fulltext:
        s = requests.Session()
        s.headers["User-Agent"] = "Mozilla/5.0 (research-news-collector)"
        for n, it in enumerate(items, 1):
            try:
                it["content"] = fetch_fulltext(s, it["url"]) or it["content"]
            except Exception as e:
                print(f"[warn] {it['url']}: {e}", file=sys.stderr)
            time.sleep(a.delay)
            print(f"\rfulltext {n}/{len(items)}", end="", file=sys.stderr)
        print(file=sys.stderr)
    if not items:
        print("수집된 기사가 없습니다.", file=sys.stderr)
        return 1
    name = f"naver_{re.sub(r'[^0-9A-Za-z가-힣]+', '_', a.keyword)}_{datetime.now():%Y%m%d}"
    print(f"saved {len(items)} articles → {save(items, Path(a.out_dir), name)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

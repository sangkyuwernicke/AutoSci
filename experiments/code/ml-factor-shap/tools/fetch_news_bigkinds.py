#!/usr/bin/env python3
"""BigKinds(빅카인즈) 기사 수집 → JSONL/CSV 저장.

사용 예:
  python tools/fetch_news_bigkinds.py --keyword 삼성전자 --start 2025-01-01 --end 2025-01-31 --max 100
  python tools/fetch_news_bigkinds.py --keyword 삼성전자 --fulltext          # 본문 전체까지 수집(느림)
  python tools/fetch_news_bigkinds.py --from-excel NewsResult.xlsx            # 웹에서 내려받은 엑셀 변환

주의:
- BigKinds 공식 오픈 API는 별도 신청(https://tools.kinds.or.kr)이 필요합니다. 이 스크립트는 웹 검색 화면이
  사용하는 비공식 엔드포인트(/api/news/search.do, /news/detailView.do)를 호출하므로 사이트 변경 시 깨질 수 있습니다.
- KRX(KIND)는 뉴스 기사가 아니라 공시를 제공합니다. 기사 수집은 BigKinds를 사용하세요.
- 이용약관/robots 및 저작권을 준수하고, 요청 간 지연(--delay)을 유지하세요.
- 저장 위치 기본값 data/news/ (실행 디렉터리 기준 상대 경로).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import requests

BASE = "https://www.bigkinds.or.kr"
SEARCH_URL = f"{BASE}/api/news/search.do"
DETAIL_URL = f"{BASE}/news/detailView.do"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (research-news-collector)",
    "Content-Type": "application/json;charset=UTF-8",
    "Referer": f"{BASE}/v2/news/index.do",
}
TAG_RE = re.compile(r"<[^>]+>")


def clean(text: str | None) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub("", text or "")).strip()


def build_payload(keyword: str, start: str, end: str, start_no: int, size: int) -> dict:
    return {
        "indexName": "news", "searchKey": keyword, "searchKeys": [{}], "byLine": "",
        "searchFilterType": "1", "searchScopeType": "1", "searchSortType": "date",
        "sortMethod": "date", "mainTodayPersonYn": "", "startDate": start, "endDate": end,
        "newsIds": [], "categoryCodes": [], "providerCodes": [], "incidentCodes": [],
        "networkNodeType": "", "topicOrigin": "", "dateCodes": [], "editorialIs": False,
        "startNo": start_no, "resultNumber": size, "isTmUsable": False, "isNotTmUsable": False,
    }


def search(session, keyword, start, end, max_items, page_size=100, delay=1.0):
    items, start_no = [], 1
    while len(items) < max_items:
        size = min(page_size, max_items - len(items))
        r = session.post(SEARCH_URL, json=build_payload(keyword, start, end, start_no, size), timeout=30)
        r.raise_for_status()
        try:
            rows = r.json().get("resultList") or []
        except ValueError:
            raise SystemExit("BigKinds가 JSON이 아닌 응답을 반환했습니다(차단/점검/엔드포인트 변경 가능). "
                             "웹에서 엑셀을 내려받아 --from-excel 을 사용하세요.")
        if not rows:
            break
        for x in rows:
            items.append({
                "id": x.get("NEWS_ID"),
                "date": x.get("DATE"),
                "provider": x.get("PROVIDER"),
                "byline": x.get("BYLINE"),
                "title": clean(x.get("TITLE")),
                "content": clean(x.get("CONTENT")),  # 검색결과 요약문
                "url": x.get("PROVIDER_LINK_PAGE") or "",
                "keyword": keyword,
            })
        start_no += 1  # BigKinds의 startNo는 페이지 번호
        time.sleep(delay)
    return items[:max_items]


def fetch_fulltext(session, news_id: str) -> str:
    r = session.get(DETAIL_URL, params={"docId": news_id, "returnCnt": 1, "sectionDiv": 1000},
                    headers={**HEADERS, "Content-Type": "text/html"}, timeout=30)
    r.raise_for_status()
    return clean((r.json().get("detail") or {}).get("CONTENT"))


def norm_date(value) -> str:
    """20151109 / 20151109.0 → 2015-11-09. 8자리 숫자가 아니면 원래 값을 문자열로 반환."""
    digits = re.sub(r"\D", "", str(value))[:8]
    return f"{digits[:4]}-{digits[4:6]}-{digits[6:8]}" if len(digits) == 8 else str(value)


def from_excel(path: str, keyword: str = "") -> list[dict]:
    """BigKinds 웹에서 '분석기사 다운로드'한 엑셀을 동일 스키마로 변환."""
    import pandas as pd
    df = pd.read_excel(path).fillna("")
    col = lambda *names: next((c for c in df.columns if c in names), None)
    c_id, c_date, c_prov = col("뉴스 식별자"), col("일자"), col("언론사")
    c_by, c_title, c_body, c_url = col("기고자"), col("제목"), col("본문"), col("URL")
    return [{
        "id": str(r[c_id]) if c_id else "", "date": norm_date(r[c_date]) if c_date else "",
        "provider": r[c_prov] if c_prov else "", "byline": r[c_by] if c_by else "",
        "title": clean(r[c_title]) if c_title else "", "content": clean(r[c_body]) if c_body else "",
        "url": r[c_url] if c_url else "", "keyword": keyword,
    } for _, r in df.iterrows()]


def save(items: list[dict], out_dir: Path, name: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    jl = out_dir / f"{name}.jsonl"
    with jl.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    import csv
    with (out_dir / f"{name}.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(items[0].keys())) if items else None
        if w:
            w.writeheader()
            w.writerows(items)
    return jl


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--keyword", help="검색어 (예: 삼성전자 / 'A AND B')")
    ap.add_argument("--start", default=(date.today() - timedelta(days=7)).isoformat())
    ap.add_argument("--end", default=date.today().isoformat())
    ap.add_argument("--max", type=int, default=100)
    ap.add_argument("--fulltext", action="store_true", help="기사 본문 전체 조회 (기사당 1회 추가 요청)")
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--from-excel", help="BigKinds 엑셀 다운로드 파일을 변환")
    ap.add_argument("--out-dir", default="data/news")
    args = ap.parse_args()

    if args.from_excel:
        items = from_excel(args.from_excel, args.keyword or "")
        name = Path(args.from_excel).stem
    else:
        if not args.keyword:
            ap.error("--keyword 또는 --from-excel 이 필요합니다")
        s = requests.Session()
        s.headers.update(HEADERS)
        s.get(f"{BASE}/v2/news/index.do", timeout=30)  # 세션 쿠키 확보
        items = search(s, args.keyword, args.start, args.end, args.max, delay=args.delay)
        if args.fulltext:
            for i, it in enumerate(items, 1):
                try:
                    it["content"] = fetch_fulltext(s, it["id"]) or it["content"]
                except Exception as e:  # 개별 실패는 요약문 유지
                    print(f"[warn] {it['id']}: {e}", file=sys.stderr)
                time.sleep(args.delay)
                print(f"\rfulltext {i}/{len(items)}", end="", file=sys.stderr)
            print(file=sys.stderr)
        name = f"bigkinds_{re.sub(r'[^0-9A-Za-z가-힣]+', '_', args.keyword)}_{args.start}_{args.end}"
    if not items:
        print("수집된 기사가 없습니다.", file=sys.stderr)
        return 1
    path = save(items, Path(args.out_dir), name)
    print(f"saved {len(items)} articles → {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

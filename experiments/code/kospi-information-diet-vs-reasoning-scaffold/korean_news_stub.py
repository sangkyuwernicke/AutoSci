"""A small, manually curated set of real news items for the pilot window.

Pilot Spec: experiments/pilot/kospi-information-diet-vs-reasoning-scaffold.yaml

This stands in for a full BigKinds/AI-Hub/Naver bulk news pipeline (flagged in
the idea's Risks section as the critical, unresolved data dependency for the
full study). It pilots that dependency at minimum viable scale: a handful of
real headlines per name, gathered via web search on 2026-09-29, summarized
here in short headline form (not verbatim scraped article text) with source
URLs for traceability.

Limitation, stated plainly: dates for the SK Hynix items are approximate
(the underlying articles describe an ongoing situation rather than a single
dated event) — marked with `date_confidence: "approximate"`. Samsung items
have exact publish dates from the search results. This is a real, not
cosmetic, gap relative to a production news pipeline with precise timestamps,
and is exactly the kind of data-quality shortfall the full study needs to
resolve via a bulk source.

Each item provides BOTH a Korean-native headline (for the D5 condition) and
an English gloss (a rough machine-translation stand-in, for the D1 condition)
— the two diet levels see the same underlying events, differing only in
whether the text is Korean-native or (naive-transfer-style) English.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NewsItem:
    date: str  # YYYY-MM-DD
    date_confidence: str  # "exact" | "approximate"
    headline_kr: str
    headline_en: str
    source_url: str


SAMSUNG_NEWS: list[NewsItem] = [
    NewsItem(
        date="2026-09-20",
        date_confidence="exact",
        headline_kr="삼성전자, 내년 HBM4·HBM4E 생산량 올해 대비 최소 2배 이상 확대 전망",
        headline_en="Samsung Electronics expected to at least double next year's HBM4/HBM4E production versus this year",
        source_url="https://www.sptatimeskorea.com/post/%EC%A0%9C20260920-tm-01%ED%98%B8-2026%EB%85%84-9%EC%9B%94-20%EC%9D%BC-%EB%B0%98%EB%8F%84%EC%B2%B4-%EC%A0%9C%EC%A1%B0-%EA%B4%80%EB%A0%A8-%EC%A3%BC%EC%9A%94-%EB%89%B4%EC%8A%A4-%EC%9A%94%EC%95%BD",
    ),
    NewsItem(
        date="2026-09-23",
        date_confidence="exact",
        headline_kr="삼성전자, 시총 1조달러 이상 기업 중 공정가치 대비 상승여력 32.7%로 1위·선행 PER 5.5배로 최저 밸류에이션",
        headline_en="Samsung Electronics leads trillion-dollar-cap peers with 32.7% upside to fair value and the lowest forward P/E (5.5x)",
        source_url="https://www.g-enews.com/article/Global-Biz/2026/09/202609241754242074fbbec65dfb_1",
    ),
    NewsItem(
        date="2026-09-26",
        date_confidence="approximate",
        headline_kr="9월 4주차 삼성전자 주가 28만원대로 상승 마감",
        headline_en="Samsung Electronics closes the 4th week of September in the KRW 280,000 range, up on the week",
        source_url="https://www.topstarnews.net/news/articleView.html?idxno=16215516",
    ),
]

SK_HYNIX_NEWS: list[NewsItem] = [
    NewsItem(
        date="2026-09-22",
        date_confidence="approximate",
        headline_kr="SK하이닉스, 미국 인디애나 HBM 생산거점 관련 부지 용도변경 무효 소송 직면 — 12월 본안 재판 예정",
        headline_en="SK Hynix's Indiana HBM production site faces a zoning-reversal lawsuit from local residents; a merits trial is set for December",
        source_url="http://www.thedailymoney.com/news/articleView.html?idxno=1136936",
    ),
    NewsItem(
        date="2026-09-15",
        date_confidence="approximate",
        headline_kr="모건스탠리, HBM 가격 상승 전망에 SK하이닉스 저평가 판단하며 목표가 상향",
        headline_en="Morgan Stanley raises its SK Hynix price target, citing rising HBM prices and calling the stock undervalued",
        source_url="https://kr.investing.com/news/stock-market-news/article-1771332",
    ),
]

NEWS_BY_NAME: dict[str, list[NewsItem]] = {
    "samsung": SAMSUNG_NEWS,
    "sk_hynix": SK_HYNIX_NEWS,
    "kodex200": [],  # no name-specific stub items; KODEX 200's D5 news slice falls back to an empty list
}


def news_as_of(name_key: str, date: str, lookback_days: int = 10) -> list[NewsItem]:
    """Items dated on or before `date`, within `lookback_days` — a look-ahead guard."""
    import pandas as pd

    cutoff = pd.Timestamp(date)
    floor = cutoff - pd.Timedelta(days=lookback_days)
    return [
        item
        for item in NEWS_BY_NAME.get(name_key, [])
        if floor <= pd.Timestamp(item.date) <= cutoff
    ]

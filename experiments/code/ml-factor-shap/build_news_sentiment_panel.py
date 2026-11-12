#!/usr/bin/env python3
"""KOSPI 종목별 일별/월별 뉴스 감성 패널 생성 (2015~2025).

입력: BigKinds 연도별 엑셀(매일경제 증권증시 전체 기사) → 기사에서 종목명을 찾아 종목별로 귀속.
출력(--out-dir, 기본 data/news/sentiment/):
  kospi_daily_sentiment.csv|parquet    long: 종목×일자 (기사가 있는 날만) n_articles/mean_score/n_pos/n_neu/n_neg
  kospi_monthly_daily_wide.csv|parquet 종목×월 한 행, s01..s31(일별 평균점수), n01..n31(일별 기사수), 뉴스 없는 날은 NaN
  article_mentions.csv                 기사×종목 매칭 내역(검수용)

  python build_news_sentiment_panel.py --years 2015            # 일부 연도만 시험
  python build_news_sentiment_panel.py                           # 2015~2025 전체
  python build_news_sentiment_panel.py --method model           # KR-FinBert-SC (느림)

주의: 기사 본문은 BigKinds 요약 200자라 매칭/감성 대상은 제목+요약뿐이다. 종목명이 2자 이하이면
`ambiguous_name=True`로 표시(그룹명/일반명사와 혼동 가능). 우선주는 제외하고 보통주만 매칭한다.
"""
from __future__ import annotations

import argparse
import glob
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent / "tools"))
from analyze_news_sentiment import label_of, lexicon_score  # noqa: E402
from fetch_news_bigkinds import from_excel  # noqa: E402

NEWS_DIR = Path("data/news/매일경제_증권증시_연도별")
MAX_AMBIGUOUS_LEN = 2
LISTING_MARGIN = pd.Timedelta(31, "D")
FINBERT = "snunlp/KR-FinBert-SC"
METHOD_DIR = {"lexicon": "lexicon", "model": "finbert"}
PARTICLES = "은는이가을를의에도와과로"
# 일반명사와 구분이 안 되어 오탐이 압도적인 이름(식품회사 '대상' ↔ 일반명사 '대상')은 매칭에서 제외
STOP_NAMES = frozenset({"대상"})


def load_articles(years: list[int]) -> pd.DataFrame:
    frames = []
    for y in years:
        path = NEWS_DIR / f"빅카인즈_매일경제_증권증시_{y}.xlsx"
        if not path.exists():
            print(f"[warn] 파일 없음: {path}", file=sys.stderr)
            continue
        frames.append(pd.DataFrame(from_excel(str(path))))
    if not frames:
        raise SystemExit("읽을 뉴스 엑셀이 없습니다.")
    df = pd.concat(frames, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["text"] = df["title"].fillna("") + " " + df["content"].fillna("")
    # 엑셀 '뉴스 식별자'는 float로 읽혀 정밀도를 잃으므로(10k건 → 고유 id 204개) 중복 판별에 쓰지 않는다.
    # URL(없으면 날짜+제목)로 중복 제거하고 기사 키는 내부 순번(aid)을 쓴다.
    df = df.drop_duplicates(["date", "title"])
    has_url = df["url"].astype(str).str.len() > 0
    df = pd.concat([df[has_url].drop_duplicates("url"), df[~has_url]])
    df = df.sort_values("date", kind="stable").reset_index(drop=True)
    df.insert(0, "aid", df.index)
    return df


def finbert_probs(texts: list[str], model_name: str = FINBERT, batch: int = 64) -> pd.DataFrame:
    """KR-FinBert-SC 확률(p_neg/p_neu/p_pos). 길이순 정렬로 패딩 낭비를 줄이고 MPS/CUDA를 자동 선택."""
    import torch
    from transformers import pipeline
    device = "mps" if torch.backends.mps.is_available() else 0 if torch.cuda.is_available() else -1
    clf = pipeline("text-classification", model=model_name, top_k=None, truncation=True,
                   max_length=512, device=device)
    order = sorted(range(len(texts)), key=lambda i: len(texts[i]))
    out = [None] * len(texts)
    for s in range(0, len(order), batch):
        idx = order[s:s + batch]
        for i, res in zip(idx, clf([texts[i] for i in idx], batch_size=batch)):
            out[i] = {r["label"].lower(): r["score"] for r in res}
        if (s // batch) % 100 == 0:
            print(f"\r  finbert {min(s + batch, len(order))}/{len(order)} (device={device})",
                  end="", file=sys.stderr, flush=True)
    print(file=sys.stderr)
    p = pd.DataFrame(out)
    return p[["negative", "neutral", "positive"]].set_axis(["p_neg", "p_neu", "p_pos"], axis=1)


def score_articles(df: pd.DataFrame, method: str, title_weight: int = 2,
                   cache: Path | None = None) -> pd.DataFrame:
    """method='lexicon' → score/label, 'model' → KR-FinBert-SC(score=p_pos-p_neg, label=argmax; 캐시 사용)."""
    if method == "lexicon":
        text = (df["title"].fillna("") + " ") * title_weight + df["content"].fillna("")
        score = text.map(lexicon_score)
        return df.assign(score=score, label=score.map(label_of))
    if cache is not None and cache.exists():
        p = pd.read_parquet(cache)
        if len(p) == len(df) and (p["aid"].to_numpy() == df["aid"].to_numpy()).all():
            print(f"finbert cache hit: {cache}")
        else:
            p = None
    else:
        p = None
    if p is None:
        probs = finbert_probs((df["title"].fillna("") + ". " + df["content"].fillna("")).str.slice(0, 1500).tolist())
        p = pd.concat([df[["aid"]].reset_index(drop=True), probs], axis=1)
        if cache is not None:
            cache.parent.mkdir(parents=True, exist_ok=True)
            p.to_parquet(cache, index=False)
    label = p[["p_neg", "p_neu", "p_pos"]].idxmax(axis=1).map(
        {"p_neg": "negative", "p_neu": "neutral", "p_pos": "positive"})
    return df.assign(score=(p["p_pos"] - p["p_neg"]).to_numpy(), label=label.to_numpy(),
                     p_neg=p["p_neg"].to_numpy(), p_neu=p["p_neu"].to_numpy(), p_pos=p["p_pos"].to_numpy())


def collect_names(marcap_dir: Path, snap_dir: Path) -> dict[str, set[str]]:
    names: dict[str, set[str]] = {}
    for f in sorted(glob.glob(str(marcap_dir / "marcap-20*.parquet"))):
        m = pd.read_parquet(f, columns=["Code", "Name", "Market"])
        for c, n in m[m.Market == "KOSPI"][["Code", "Name"]].drop_duplicates().itertuples(index=False):
            names.setdefault(c, set()).add(n)
    for f in sorted(glob.glob(str(snap_dir / "*.csv"))):
        s = pd.read_csv(f, encoding="utf-8-sig", dtype={"종목코드": str})
        for c, n in s[s["시장구분"].str.contains("KOSPI")][["종목코드", "종목명"]].itertuples(index=False):
            names.setdefault(c, set()).add(n)
    return names


def load_universe(prices_path: Path, marcap_dir: Path, snap_dir: Path) -> pd.DataFrame:
    """KOSPI 보통주별 (ticker, name, 상장 시작~종료일). 이름은 marcap/스냅샷의 이력 전체."""
    p = pd.read_parquet(prices_path, columns=["date", "ticker", "market"])
    k = p[p.market == "KOSPI"]
    # 보통주 코드는 끝자리 0. 신형 코드(영문 포함)는 보통주로 유지
    k = k[k.ticker.str.endswith("0") | k.ticker.str.contains(r"[A-Z]", regex=True)]
    span = k.groupby("ticker")["date"].agg(first="min", last="max").reset_index()

    names = collect_names(marcap_dir, snap_dir)
    rows = [(t, n, a, b) for t, a, b in span[["ticker", "first", "last"]].itertuples(index=False)
            for n in names.get(t, ())]
    uni = pd.DataFrame(rows, columns=["ticker", "name", "first", "last"])
    uni["name"] = uni["name"].str.replace(r"\(주\)|\s", "", regex=True)
    uni = uni[~uni["name"].str.contains(r"스팩|\d+호$|우$|우B$|우\(전환\)$", regex=True)]
    uni["ambiguous_name"] = uni["name"].str.len() <= MAX_AMBIGUOUS_LEN
    return uni.drop_duplicates(["ticker", "name"]).reset_index(drop=True)


def name_regex(name: str) -> str:
    """영문/숫자로 시작하는 이름은 왼쪽 경계(ELS 안의 LS 방지), 2자 이하 이름은 오른쪽 경계
    (신흥국·선진국 안의 신흥/선진 방지)를 둔다. 한글 조사가 바로 뒤따르는 경우는 허용."""
    body = re.escape(name)
    if len(name) <= MAX_AMBIGUOUS_LEN:
        body = rf"{body}(?:(?![가-힣])|(?=[{PARTICLES}]))"
    left = r"(?<![A-Za-z0-9])" if name[0].isascii() and name[0].isalnum() else ""
    return left + body


def match_mentions(arts: pd.DataFrame, uni: pd.DataFrame) -> pd.DataFrame:
    """기사 텍스트에서 종목명 매칭. 긴 이름 우선 alternation이라 'SK하이닉스' 안의 'SK'는 잡히지 않는다.
    상장 기간(±31일) 밖 매칭은 버린다."""
    by_name = {n: g for n, g in uni.groupby("name") if n not in STOP_NAMES}
    pattern = re.compile("|".join(name_regex(n) for n in sorted(by_name, key=len, reverse=True)))
    rows = []
    for aid, date, text in arts[["aid", "date", "text"]].itertuples(index=False):
        for name in set(pattern.findall(text)):
            for r in by_name[name].itertuples(index=False):
                if r.first - LISTING_MARGIN <= date <= r.last + LISTING_MARGIN:
                    rows.append((aid, date, r.ticker, name, r.ambiguous_name))
    return pd.DataFrame(rows, columns=["aid", "date", "ticker", "name", "ambiguous_name"])


def daily_panel(arts: pd.DataFrame, mentions: pd.DataFrame) -> pd.DataFrame:
    # 개명 종목은 한 기사가 옛/새 이름으로 두 번 매칭될 수 있으므로 (기사, 종목)당 1건으로 합친다.
    m = (mentions.groupby(["aid", "ticker", "date"], as_index=False)
                 .agg(name=("name", lambda s: "/".join(sorted(set(s)))),
                      ambiguous_name=("ambiguous_name", "all")))
    j = m.merge(arts[["aid", "score", "label"]], on="aid")
    j = j.assign(is_pos=j["label"] == "positive", is_neu=j["label"] == "neutral",
                 is_neg=j["label"] == "negative")
    # 같은 종목이 날짜별로 다른 이름 조합을 가질 수 있으므로 (종목, 날짜)로만 집계하고 이름은 이어붙인다.
    out = (j.groupby(["ticker", "date"], as_index=False)
             .agg(name=("name", lambda s: "/".join(sorted(set("/".join(s).split("/"))))),
                  ambiguous_name=("ambiguous_name", "all"),
                  n_articles=("aid", "nunique"), mean_score=("score", "mean"),
                  n_pos=("is_pos", "sum"), n_neu=("is_neu", "sum"), n_neg=("is_neg", "sum")))
    return out.sort_values(["ticker", "date"]).reset_index(drop=True)


def monthly_wide(daily: pd.DataFrame) -> pd.DataFrame:
    d = daily.assign(month=daily["date"].dt.to_period("M").astype(str), day=daily["date"].dt.day)
    s = d.pivot_table(index=["ticker", "month"], columns="day", values="mean_score")
    n = d.pivot_table(index=["ticker", "month"], columns="day", values="n_articles")
    s = s.reindex(columns=range(1, 32)).rename(columns=lambda c: f"s{c:02d}")
    n = n.reindex(columns=range(1, 32)).rename(columns=lambda c: f"n{c:02d}")
    w = pd.concat([s, n], axis=1)
    w.insert(0, "n_articles_month", n.fillna(0).sum(axis=1).astype(int))
    w = w.reset_index()
    names = daily.groupby("ticker")["name"].agg(lambda x: "/".join(sorted(set(x))))
    w.insert(1, "name", w["ticker"].map(names))
    return w


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--years", type=int, nargs="+", default=list(range(2015, 2026)))
    ap.add_argument("--method", choices=["lexicon", "model", "both"], default="model",
                    help="model(default): KR-FinBert-SC, the sentiment index used by the experiment. lexicon/both are "
                         "kept only for the method-comparison study (both -> <out>/lexicon, <out>/finbert)")
    ap.add_argument("--prices", default="data/real/prices.parquet")
    ap.add_argument("--marcap-dir", default="data/marcap/data")
    ap.add_argument("--snap-dir", default="data/krx/snapshots")
    ap.add_argument("--out-dir", default="data/news/sentiment")
    args = ap.parse_args()

    out = Path(args.out_dir)
    base = load_articles(args.years)
    print(f"articles(dedup)={len(base)}  years={args.years[0]}~{args.years[-1]}")
    uni = load_universe(Path(args.prices), Path(args.marcap_dir), Path(args.snap_dir))
    print(f"universe: tickers={uni.ticker.nunique()} names={uni.name.nunique()}")
    mentions = match_mentions(base, uni)  # 매칭은 점수와 무관하므로 한 번만
    print(f"mentions={len(mentions)}  tickers_with_news={mentions.ticker.nunique()}")

    methods = ["lexicon", "model"] if args.method == "both" else [args.method]
    scored = {}
    for m in methods:
        cache = out / "finbert_article_probs.parquet" if m == "model" else None
        scored[m] = score_articles(base, m, cache=cache)
        sub = out / METHOD_DIR[m] if args.method == "both" else out
        write_panel(scored[m], mentions, sub)
    if args.method == "both":
        lex, fb = scored["lexicon"], scored["model"]
        art = base[["aid", "date", "title", "url"]].assign(
            score_lex=lex["score"].to_numpy(), label_lex=lex["label"].to_numpy(),
            score_fb=fb["score"].to_numpy(), label_fb=fb["label"].to_numpy(),
            p_neg=fb["p_neg"].to_numpy(), p_neu=fb["p_neu"].to_numpy(), p_pos=fb["p_pos"].to_numpy())
        art.to_parquet(out / "article_scores.parquet", index=False)
        print(f"article_scores.parquet rows={len(art)}")
    return 0


def write_panel(arts: pd.DataFrame, mentions: pd.DataFrame, out: Path) -> None:
    daily = daily_panel(arts, mentions)
    wide = monthly_wide(daily)
    out.mkdir(parents=True, exist_ok=True)
    for name, df in (("kospi_daily_sentiment", daily), ("kospi_monthly_daily_wide", wide)):
        df.to_csv(out / f"{name}.csv", index=False, encoding="utf-8-sig")
        df.to_parquet(out / f"{name}.parquet", index=False)
    audit = mentions.merge(arts[["aid", "title", "url", "score"]], on="aid")
    audit.to_csv(out / "article_mentions.csv", index=False, encoding="utf-8-sig")
    print(f"daily rows={len(daily)}  monthly rows={len(wide)}\nsaved → {out}/")


if __name__ == "__main__":
    sys.exit(main())

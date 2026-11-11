#!/usr/bin/env python3
"""저장된 기사(JSONL/CSV)의 감성 분석.

  python tools/analyze_news_sentiment.py raw/tmp/news/xxx.jsonl                   # 사전 기반(의존성 없음)
  python tools/analyze_news_sentiment.py raw/tmp/news/xxx.jsonl --method model    # KR-FinBert-SC (transformers 필요)

결과: <입력>.sentiment.csv (기사별 label/score) + 콘솔 요약(전체 분포, 일자별 평균).
score ∈ [-1, 1], label ∈ {positive, neutral, negative}.
model 방식은 `pip install transformers torch` 필요. 기본 모델 snunlp/KR-FinBert-SC(금융 뉴스 도메인).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

# 금융/주식 뉴스용 간이 사전 (필요 시 확장). 어간 부분일치로 매칭.
POS = """상승 급등 호조 호실적 흑자 개선 증가 성장 확대 최대 신기록 사상최고 돌파 반등 회복 수혜 기대 강세 우수 달성
성공 수주 상향 배당 매수 낙관 호재 혁신 흑자전환 약진 선전 순항 개선세 증가세 반색""".split()
NEG = """하락 급락 부진 적자 악화 감소 위기 축소 최저 폭락 침체 우려 약세 손실 하향 매도 비관 악재 리스크 불안
논란 소송 제재 과징금 횡령 배임 상장폐지 부도 파산 쇼크 충격 적자전환 급감 둔화 경고 취소 지연 중단""".split()
NEGATORS = ("않", "못", "아니", "없")  # '개선되지 않' 등 간단한 부정 처리


def lexicon_score(text: str) -> float:
    pos = neg = 0
    for w in POS + NEG:
        for m in re.finditer(re.escape(w), text):
            tail = text[m.end(): m.end() + 6]
            sign = 1 if w in POS else -1
            if any(n in tail for n in NEGATORS):
                sign = -sign
            pos += sign > 0
            neg += sign < 0
    total = pos + neg
    return 0.0 if total == 0 else (pos - neg) / total


def label_of(score: float, th: float = 0.15) -> str:
    return "positive" if score > th else "negative" if score < -th else "neutral"


def load(path: Path) -> pd.DataFrame:
    if path.suffix == ".jsonl":
        return pd.DataFrame([json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()])
    return pd.read_csv(path, encoding="utf-8-sig")


def model_scores(texts: list[str], model_name: str, batch: int = 16) -> list[tuple[str, float]]:
    from transformers import pipeline
    clf = pipeline("text-classification", model=model_name, top_k=None, truncation=True, max_length=512)
    out = []
    for i in range(0, len(texts), batch):
        for res in clf(texts[i:i + batch]):
            p = {r["label"].lower(): r["score"] for r in res}
            score = p.get("positive", 0.0) - p.get("negative", 0.0)
            out.append((max(p, key=p.get), score))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("--method", choices=["lexicon", "model"], default="lexicon")
    ap.add_argument("--model", default="snunlp/KR-FinBert-SC")
    ap.add_argument("--title-weight", type=int, default=2, help="제목 반복 횟수(제목 가중치)")
    ap.add_argument("--output")
    args = ap.parse_args()

    p = Path(args.input)
    df = load(p)
    for c in ("title", "content"):
        df[c] = df.get(c, "").fillna("").astype(str)
    if args.method == "lexicon":
        df["text"] = (df["title"] + " ") * args.title_weight + df["content"]
        df["score"] = df["text"].map(lexicon_score)
        df["label"] = df["score"].map(label_of)
    else:
        texts = (df["title"] + ". " + df["content"]).str.slice(0, 1500).tolist()
        res = model_scores(texts, args.model)
        df["label"], df["score"] = [r[0] for r in res], [r[1] for r in res]
    df = df.drop(columns=["text"], errors="ignore")

    out = Path(args.output) if args.output else p.with_suffix(".sentiment.csv")
    df.to_csv(out, index=False, encoding="utf-8-sig")

    print(f"articles={len(df)}  mean_score={df['score'].mean():+.3f}")
    print(df["label"].value_counts().to_string())
    if "date" in df:
        d = pd.to_datetime(df["date"].astype(str).str[:10], errors="coerce")
        daily = df.groupby(d.dt.date)["score"].agg(["mean", "count"]).dropna()
        if len(daily):
            print("\n일자별 평균 감성:\n" + daily.round(3).to_string())
    print(f"\nsaved → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

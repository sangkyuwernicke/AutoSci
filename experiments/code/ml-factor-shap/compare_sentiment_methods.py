#!/usr/bin/env python3
"""사전(lexicon) vs KR-FinBert-SC 감성 비교 (기사 / 종목-일 / 수익률 예측 타당성).

  python build_news_sentiment_panel.py --method both --out-dir data/news/sentiment_cmp
  python compare_sentiment_methods.py --in-dir data/news/sentiment_cmp --out results/news_sentiment_compare

산출: <out>/summary.md 와 표 CSV들. 수익률은 prices.parquet 종가 기준.
look-ahead 주의: 뉴스일 d의 '선행' 수익률은 d 이전(포함) 마지막 거래일 t의 종가에서 t+1 / t+5 종가까지이며,
당일(t-1→t) 수익률은 선행이 아닌 동행(감성이 가격을 따라가는지) 참고용이다.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import cohen_kappa_score

LABELS = ["negative", "neutral", "positive"]
MIN_STOCKS_PER_DAY = 8
EXAMPLE_N = 15


def article_agreement(art: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    dist = pd.DataFrame({
        "lexicon": art["label_lex"].value_counts(normalize=True),
        "finbert": art["label_fb"].value_counts(normalize=True)}).reindex(LABELS)
    conf = pd.crosstab(art["label_lex"], art["label_fb"]).reindex(index=LABELS, columns=LABELS, fill_value=0)
    stat = {
        "n_articles": len(art),
        "agreement": float((art["label_lex"] == art["label_fb"]).mean()),
        "cohen_kappa": float(cohen_kappa_score(art["label_lex"], art["label_fb"])),
        "pearson": float(art["score_lex"].corr(art["score_fb"])),
        "spearman": float(stats.spearmanr(art["score_lex"], art["score_fb"])[0]),
        "mean_lex": float(art["score_lex"].mean()), "mean_fb": float(art["score_fb"].mean()),
        "std_lex": float(art["score_lex"].std()), "std_fb": float(art["score_fb"].std()),
    }
    return dist, conf, stat


def disagreement_examples(art: pd.DataFrame) -> pd.DataFrame:
    """두 방법이 극단적으로 반대인 기사(검수/논문 사례용)."""
    gap = (art["score_lex"] - art["score_fb"]).abs()
    cols = ["date", "title", "score_lex", "score_fb", "label_lex", "label_fb"]
    return art.assign(gap=gap).nlargest(EXAMPLE_N, "gap")[cols + ["gap"]]


def ticker_day_agreement(lex: pd.DataFrame, fb: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    m = lex.merge(fb, on=["ticker", "date"], suffixes=("_lex", "_fb"))
    sign = np.sign(m["mean_score_lex"]) == np.sign(m["mean_score_fb"])
    stat = {
        "n_ticker_days": len(m),
        "pearson": float(m["mean_score_lex"].corr(m["mean_score_fb"])),
        "spearman": float(stats.spearmanr(m["mean_score_lex"], m["mean_score_fb"])[0]),
        "sign_agreement": float(sign.mean()),
        "lex_share_exact_-1_0_1": float(m["mean_score_lex"].round(6).isin([-1, 0, 1]).mean()),
        "fb_share_exact_-1_0_1": float(m["mean_score_fb"].round(6).isin([-1, 0, 1]).mean()),
    }
    return m, stat


def return_matrices(prices: pd.DataFrame, tickers: set[str]) -> dict[str, pd.DataFrame]:
    px = prices[prices.ticker.isin(tickers)].pivot(index="date", columns="ticker", values="close").sort_index()
    return {"ret0": px / px.shift(1) - 1, "fwd1": px.shift(-1) / px - 1, "fwd5": px.shift(-5) / px - 1}


def attach_returns(panel: pd.DataFrame, rets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """뉴스일 d → d 이전(포함) 마지막 거래일 t 기준 수익률을 붙인다."""
    cal = rets["ret0"].index
    pos = cal.searchsorted(panel["date"].to_numpy(), side="right") - 1
    ok = pos >= 0
    out = panel[ok].copy()
    t = cal[pos[ok]]
    for k, wide in rets.items():
        out[k] = [wide.at[d, tk] if tk in wide.columns else np.nan for d, tk in zip(t, out["ticker"])]
    return out


def rank_ic(df: pd.DataFrame, score: str, ret: str) -> dict:
    """날짜별 횡단면 Spearman IC의 평균/t값 + 날짜 평균 제거 후 pooled 상관."""
    d = df.dropna(subset=[score, ret])
    per_day = d.groupby("date").filter(lambda g: len(g) >= MIN_STOCKS_PER_DAY)
    ic = per_day.groupby("date").apply(lambda g: stats.spearmanr(g[score], g[ret])[0],
                                       include_groups=False).dropna()
    dm = d[ret] - d.groupby("date")[ret].transform("mean")
    return {"n_days": len(ic), "mean_ic": float(ic.mean()),
            "t_stat": float(ic.mean() / ic.std(ddof=1) * np.sqrt(len(ic))),
            "hit_rate": float((ic > 0).mean()),
            "pooled_spearman": float(stats.spearmanr(d[score], dm)[0]), "n_obs": len(d)}


def predictive_table(merged: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    df = attach_returns(merged, return_matrices(prices, set(merged["ticker"])))
    rows = []
    for method, col in (("lexicon", "mean_score_lex"), ("finbert", "mean_score_fb")):
        for ret, kind in (("ret0", "동행(당일)"), ("fwd1", "선행 1일"), ("fwd5", "선행 5일")):
            rows.append({"method": method, "horizon": kind, **rank_ic(df, col, ret)})
    return pd.DataFrame(rows)


def to_markdown(dist, conf, art_stat, td_stat, pred) -> str:
    f = lambda d: d.to_markdown(floatfmt=".3f")  # noqa: E731
    td = [f"- {k}: {v:.3f}" if isinstance(v, float) else f"- {k}: {v:,}" for k, v in td_stat.items()]
    lines = [
        "# 뉴스 감성: 사전(lexicon) vs KR-FinBert-SC", "",
        "## 1. 기사 단위 일치도",
        f"- 기사 수 {art_stat['n_articles']:,}  / 라벨 일치율 {art_stat['agreement']:.3f}  "
        f"/ Cohen's κ {art_stat['cohen_kappa']:.3f}",
        f"- 점수 상관: Pearson {art_stat['pearson']:.3f}, Spearman {art_stat['spearman']:.3f}",
        f"- 평균(표준편차): lexicon {art_stat['mean_lex']:+.3f} ({art_stat['std_lex']:.3f}), "
        f"FinBert {art_stat['mean_fb']:+.3f} ({art_stat['std_fb']:.3f})", "",
        "### 라벨 분포", f(dist), "", "### 혼동행렬 (행=lexicon, 열=FinBert)", f(conf), "",
        "## 2. 종목-일 단위 일치도", *td, "",
        "## 3. 수익률 예측 타당성 (날짜별 횡단면 rank IC)",
        f"일별 최소 {MIN_STOCKS_PER_DAY}종목 이상인 날만 사용. t값은 날짜 간 독립 가정(단순 t).", "",
        f(pred.set_index(["method", "horizon"]))]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in-dir", default="data/news/sentiment_cmp")
    ap.add_argument("--prices", default="data/real/prices.parquet")
    ap.add_argument("--out", default="results/news_sentiment_compare")
    args = ap.parse_args()
    ind, out = Path(args.in_dir), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    art = pd.read_parquet(ind / "article_scores.parquet")
    dist, conf, art_stat = article_agreement(art)
    lex = pd.read_parquet(ind / "lexicon" / "kospi_daily_sentiment.parquet")[["ticker", "date", "n_articles", "mean_score"]]
    fb = pd.read_parquet(ind / "finbert" / "kospi_daily_sentiment.parquet")[["ticker", "date", "mean_score"]]
    merged, td_stat = ticker_day_agreement(lex, fb)
    pred = predictive_table(merged, pd.read_parquet(args.prices, columns=["date", "ticker", "close"]))

    dist.to_csv(out / "label_distribution.csv", encoding="utf-8-sig")
    conf.to_csv(out / "confusion_matrix.csv", encoding="utf-8-sig")
    pred.to_csv(out / "predictive_ic.csv", index=False, encoding="utf-8-sig")
    disagreement_examples(art).to_csv(out / "disagreement_examples.csv", index=False, encoding="utf-8-sig")
    (out / "summary.md").write_text(to_markdown(dist, conf, art_stat, td_stat, pred), encoding="utf-8")
    print((out / "summary.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

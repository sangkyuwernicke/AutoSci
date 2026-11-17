"""compare_outlets: pooling is article-weighted, pairwise agreement uses only shared (ticker, date)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import compare_outlets as co  # noqa: E402


def mk(rows):
    d = pd.DataFrame(rows, columns=["ticker", "date", "n_articles", "mean_score"])
    d["date"] = pd.to_datetime(d["date"])
    return d


def test_pool_is_article_weighted():
    a = mk([("000001", "2024-01-02", 1, 1.0), ("000002", "2024-01-02", 2, 0.5)])
    b = mk([("000001", "2024-01-02", 3, -1.0)])
    p = co.pool({"a": a, "b": b}).set_index("ticker")
    assert p.loc["000001", "n_articles"] == 4
    assert abs(p.loc["000001", "mean_score"] - (1.0 - 3.0) / 4) < 1e-12
    assert p.loc["000002", "n_articles"] == 2 and abs(p.loc["000002", "mean_score"] - 0.5) < 1e-12


def test_agreement_only_on_shared_keys():
    rng = np.random.default_rng(0)
    t = [f"{i:06d}" for i in range(40)]
    s = rng.uniform(-1, 1, 40)
    a = mk([(k, "2024-01-02", 1, v) for k, v in zip(t, s)])
    b = mk([(k, "2024-01-02", 1, v) for k, v in zip(t[:30], s[:30])] + [("999999", "2024-01-02", 1, 0.3)])
    r = co.pair_agreement(a, b)
    assert r["n_shared"] == 30 and abs(r["pearson"] - 1) < 1e-9 and r["sign_agree"] == 1.0


def test_coverage_by_year():
    a = mk([("000001", "2023-05-01", 2, 0.1), ("000001", "2024-05-01", 1, 0.1), ("000002", "2024-05-02", 1, 0.1)])
    c = co.coverage(a).set_index("year")
    assert c.loc[2024, "ticker_days"] == 2 and c.loc[2024, "n_articles"] == 2 and c.loc[2023, "tickers"] == 1


if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v()
    print("ALL PASS")

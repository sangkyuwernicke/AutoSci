"""Top-k selection and KOSPI200 proxy. Run: python tests/test_topk.py"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import evaluation as ev

assert ev.select_k(650, 200) == 200 and ev.select_k(150, 200) == 150      # count, capped at the universe
assert ev.select_k(650, 0.2) == 130 and ev.select_k(3, 0.2) == 1           # fraction

rng = np.random.default_rng(0)
rows = []
for d in pd.to_datetime(["2023-01-31", "2023-02-28"]):
    for i in range(300):
        rows.append(dict(date=d, ticker=f"{i:06d}", y=int(rng.random() > .5), score=rng.random(),
                         ret_next=rng.normal(0, .05), mkt_next=0.01, mcap=float(300 - i)))
pred = pd.DataFrame(rows)
bt = ev.backtest(pred, 200, 0.002)
g = pred[pred.date == "2023-01-31"]
assert abs(bt.loc["2023-01-31", "gross"] - g.nlargest(200, "score")["ret_next"].mean()) < 1e-12
k = ev.cap_weighted_top(pred, 200)
t = g.nlargest(200, "mcap")
assert abs(k["2023-01-31"] - (t.ret_next * t.mcap).sum() / t.mcap.sum()) < 1e-12
print("topk tests passed")

"""Monthly-AUC tuning objective and seeded tie-breaking. Run: python tests/test_tune_metric.py"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import evaluation as ev
from models import monthly_auc

rng = np.random.default_rng(0)
months = np.repeat(pd.to_datetime(["2023-01-31", "2023-02-28", "2023-03-31", "2023-04-30"]), 200)
# month 1,2: market-wide up (80% of stocks rise), month 3,4: down (20%): the month level is predictable, the cross-section is not
y = np.concatenate([(rng.random(200) < p).astype(int) for p in (.8, .8, .2, .2)])
macro_only = np.repeat([.8, .8, .2, .2], 200)                     # one score per month, perfectly tracks the month level
informed = y + rng.normal(0, 1.0, len(y))                         # cross-sectional signal, weak

assert roc_auc_score(y, macro_only) > 0.7                         # pooled AUC loves the macro-only score
assert abs(monthly_auc(y, macro_only, months) - 0.5) < 1e-12      # monthly AUC gives it nothing
assert monthly_auc(y, informed, months) > 0.6                     # but rewards real cross-sectional skill

# ties: the chosen stocks must not be the first rows of the frame
df = pd.DataFrame(dict(date=pd.Timestamp("2023-01-31"), ticker=[f"{i:06d}" for i in range(300)], y=0,
                       ret_next=0.0, mkt_next=0.0, score=0.5))
top = ev.rank_desc(df).iloc[:50]["ticker"]
assert set(top) != set(df["ticker"].iloc[:50]) and len(set(top)) == 50
assert list(ev.rank_desc(df)["ticker"]) == list(ev.rank_desc(df)["ticker"])      # deterministic
df2 = df.assign(score=np.linspace(0, 1, 300))
assert list(ev.rank_desc(df2).iloc[:3]["ticker"]) == ["000299", "000298", "000297"]   # no ties: plain ordering
print("tune metric tests passed")

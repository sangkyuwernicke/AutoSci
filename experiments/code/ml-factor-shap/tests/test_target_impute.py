"""Direction target and forward-fill imputation (no look-ahead)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from features import add_target, impute_ffill


def _panel():
    d = pd.date_range("2021-01-31", periods=4, freq="ME")
    p = pd.DataFrame({"date": np.repeat(d, 2), "ticker": ["A", "B"] * 4})
    p["ret_next"] = [0.05, -0.02, -0.01, -0.03, 0.02, 0.01, -0.04, 0.03]
    p["mkt_next"] = 0.0
    return p


def test_direction_label_is_absolute():
    y = add_target(_panel(), direction=True)["y"].tolist()
    assert y == [1, 0, 0, 0, 1, 1, 0, 1]          # sign of own return; unaffected by the cross-section


def test_ffill_never_backfills_and_drops_dead_factor():
    p = _panel()
    p["F"] = [np.nan, 1, 2, 1, np.nan, 1, 4, 1]    # A: first value missing, later gap
    p["DEAD"] = np.nan
    q, kept, rep = impute_ffill(p, ["F", "DEAD"], max_missing=0.3)
    a = q[q.ticker == "A"].sort_values("date")["F"].tolist()
    assert np.isnan(a[0]) and a[1:] == [2, 2, 4]   # leading gap stays NaN (no back-fill); later gap uses last value
    assert kept == ["F"] and not rep.loc["DEAD", "kept"]


if __name__ == "__main__":
    test_direction_label_is_absolute()
    test_ffill_never_backfills_and_drops_dead_factor()
    print("target/imputation tests passed")

"""Unit tests for RegimeGatedScorer and --macro-role gating functionality."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import RegimeGatedScorer, build, suggest
from features import add_target, cross_sectional_transform
from data_synth import make_synthetic_panel
from config import BASE_FACTORS, MACRO


def test_regime_gated_scorer():
    firm_cols = BASE_FACTORS[:4]
    macro_cols = MACRO[:3]

    panel = make_synthetic_panel(n_stocks=20, start="2022-01-31", end="2023-12-31")
    panel = add_target(panel)
    panel = cross_sectional_transform(panel, firm_cols)

    X = panel[firm_cols + macro_cols]
    y = panel["y"]

    scorer = RegimeGatedScorer(firm_cols=firm_cols, macro_cols=macro_cols, n_regimes=2, C=1.0)
    scorer.fit(X, y)

    probs = scorer.predict_proba(X)
    assert probs.shape == (len(X), 2), f"Expected shape {(len(X), 2)}, got {probs.shape}"
    assert np.all((probs >= 0.0) & (probs <= 1.0)), "Probabilities out of bounds"
    assert np.allclose(probs.sum(axis=1), 1.0), "Probabilities do not sum to 1"

    preds = scorer.predict(X)
    assert set(np.unique(preds)).issubset({0, 1})

    # Test factor weights extraction
    sample_macro = X[macro_cols].iloc[0].values
    fw = scorer.factor_weights(sample_macro)
    assert isinstance(fw, pd.Series)
    assert len(fw) == len(firm_cols)
    assert set(fw.index) == set(firm_cols)

    # Test regime centroids extraction
    centroids = scorer.regime_centroids_df()
    assert centroids.shape == (2, len(macro_cols))

    print("test_regime_gated_scorer passed")


if __name__ == "__main__":
    test_regime_gated_scorer()

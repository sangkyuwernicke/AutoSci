"""Synthetic monthly panel with a *known* regime-dependent factor structure.

Purpose: verify the whole pipeline end to end without API keys. The data-generating
process makes factor payoffs depend on the macro regime (value/quality pay in high-rate
regimes, growth in low-rate regimes, momentum flips when the curve is inverted, plus a
value x quality interaction), so H1-H3 have a ground truth to recover. Results on this
data say nothing about the Korean market.
"""
import numpy as np
import pandas as pd

from config import MACRO


def _macro_path(dates, rng):
    x = dates.map(pd.Timestamp.toordinal).to_numpy(dtype=float)

    def interp(anchors):
        ks = [pd.Timestamp(k).toordinal() for k in anchors]
        return np.interp(x, ks, list(anchors.values()))

    def ar1(n, phi, sd):
        e = np.zeros(n)
        for i in range(1, n):
            e[i] = phi * e[i - 1] + rng.normal(0, sd)
        return e

    n = len(dates)
    base = interp({"2013-12-31": 2.5, "2016-06-30": 1.25, "2018-11-30": 1.75, "2020-06-30": 0.5,
                   "2021-12-31": 1.0, "2023-01-31": 3.5, "2024-09-30": 3.5, "2025-12-31": 2.5})
    spread = interp({"2013-12-31": 1.0, "2019-06-30": 0.2, "2021-03-31": 1.0, "2022-12-31": -0.4,
                     "2024-06-30": -0.1, "2025-12-31": 0.4}) + ar1(n, 0.8, 0.08)
    cpi = interp({"2013-12-31": 1.3, "2020-06-30": 0.3, "2022-07-31": 6.0, "2024-06-30": 2.5,
                  "2025-12-31": 2.1}) + ar1(n, 0.7, 0.15)
    fx = interp({"2013-12-31": 1050, "2016-12-31": 1200, "2021-06-30": 1120,
                 "2022-10-31": 1420, "2025-12-31": 1400}) * np.exp(ar1(n, 0.6, 0.01))
    vk = interp({"2013-12-31": 15, "2020-03-31": 40, "2020-09-30": 22, "2022-10-31": 28,
                 "2025-12-31": 17}) * np.exp(ar1(n, 0.7, 0.08))
    return pd.DataFrame({"BASE_RATE": base, "TERM_SPREAD": spread, "CPI_YOY": cpi,
                         "KRWUSD": fx, "VKOSPI": vk}, index=dates)


def make_synthetic_panel(n_stocks=300, seed=0, start="2013-12-31", end="2025-12-31",
                         signal_strength=1.5):
    """Rows are (feature date t, ticker); ret_next is the return over month t+1."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start, end, freq="ME")
    T, N, H = len(dates), n_stocks, 12
    macro = _macro_path(dates, rng)

    # slow-moving latent firm characteristics: value, profitability, growth, quality
    K, phi = 4, 0.92
    lat = np.zeros((T, N, K))
    lat[0] = rng.normal(size=(N, K))
    for t in range(1, T):
        lat[t] = phi * lat[t - 1] + np.sqrt(1 - phi ** 2) * rng.normal(size=(N, K))
    stock_vol = np.exp(rng.normal(0, 0.3, N))

    R = np.zeros((T + H, N))                      # R[H+k] = return over month after date k
    R[:H] = rng.normal(0.005, 0.08, (H, N))       # pre-sample history for momentum
    rows = []
    for k in range(T):
        v, p, g, q = lat[k].T
        hist = R[k:H + k]                         # the 12 months realised up to date k
        r1, r3 = hist[-1], np.prod(1 + hist[-3:], axis=0) - 1
        r12 = np.prod(1 + hist, axis=0) - 1
        m3 = (r3 - r3.mean()) / (r3.std() + 1e-9)

        m = macro.iloc[k]
        hr = 1 / (1 + np.exp(-(m.BASE_RATE - 2.0) / 0.5))       # high-rate regime weight
        inv = 1 / (1 + np.exp((m.TERM_SPREAD - 0.2) / 0.15))    # inverted/flat curve weight
        s = (v * (0.002 + 0.006 * hr) + p * 0.004 + g * 0.006 * (1 - hr)
             + q * (0.001 + 0.006 * hr) + m3 * 0.004 * (1 - 2 * inv) + 0.003 * v * q)
        noise = 0.07 * stock_vol * rng.standard_t(4, N) / np.sqrt(2)
        R[H + k] = 0.006 + rng.normal(0, 0.04) + signal_strength * s + noise

        e = lambda sd=0.25: rng.normal(0, sd, N)
        vol = stock_vol * 0.02 * (m.VKOSPI / 18) * np.exp(e(0.2))
        f = pd.DataFrame({
            "date": dates[k], "ticker": [f"S{i:04d}" for i in range(N)],
            "PER": 12 * np.exp(-0.5 * v + e()), "PBR": 1.0 * np.exp(-0.5 * v + e()),
            "PCR": 8 * np.exp(-0.5 * v + e()), "EV_EBITDA": 8 * np.exp(-0.4 * v + e()),
            "ROE": 0.08 + 0.06 * p + 0.03 * e(1), "ROA": 0.04 + 0.03 * p + 0.015 * e(1),
            "OPM": 0.07 + 0.05 * p + 0.03 * e(1), "GPOA": 0.25 + 0.1 * p + 0.05 * e(1),
            "SALES_GROWTH": 0.05 + 0.15 * g + 0.05 * e(1), "OP_GROWTH": 0.05 + 0.4 * g + 0.2 * e(1),
            "DEBT_RATIO": 100 * np.exp(-0.4 * q + e()), "QUICK_RATIO": 1.2 * np.exp(0.3 * q + e()),
            "ICR": 5 * np.exp(0.6 * q + e(0.4)),
            "RET_1M": r1, "RET_3M": r3, "RET_12M": r12, "VOL_20D": vol,
        })
        for c in MACRO:
            f[c] = m[c]
        rows.append(f)

    panel = pd.concat(rows, ignore_index=True)
    ret_next = R[H:].reshape(-1)                  # same (date-major, ticker-minor) order
    panel["ret_next"] = ret_next
    panel["mkt_next"] = panel.groupby("date")["ret_next"].transform("mean")

    # dirty the data: outliers, negative earnings, missing values
    feat = [c for c in panel.columns if c not in ("date", "ticker", "ret_next", "mkt_next") and c not in MACRO]
    for c in feat:
        panel.loc[rng.random(len(panel)) < 0.005, c] *= rng.choice([-20, 20], 1)[0]
        panel.loc[rng.random(len(panel)) < 0.02, c] = np.nan
    return panel

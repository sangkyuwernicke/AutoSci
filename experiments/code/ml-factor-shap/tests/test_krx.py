"""KRX hand-download path: prepare_krx.py -> prices_monthly/index -> build_panel(market=...).
Run: python tests/test_krx.py"""
import sys, tempfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import MACRO
from data_real import build_panel
from prepare_krx import build_monthly, load_index, load_snapshots

HDR = "기준일자,종목코드,종목명,시장구분,종가,대비,등락률,시가,고가,저가,거래량,거래대금,시가총액,상장주식수"
MONTHS = pd.date_range("2019-12-31", "2022-12-31", freq="ME")
rng = np.random.default_rng(0)
# code, name, market, listed months (index slice), shares, special
STOCKS = [("000010", "에이전자", "KOSPI"), ("000015", "에이전자우", "KOSPI"), ("000020", "케이금융지주", "KOSPI"),
          ("000030", "비코스닥", "KOSDAQ"), ("000040", "분할기업", "KOSPI"), ("000050", "결측월기업", "KOSPI"),
          ("000060", "상폐기업", "KOSPI"), ("000070", "삼호스팩", "KOSPI"), ("000080", "정상기업", "KOSPI")]


def write(krx):
    snap = krx / "snapshots"; snap.mkdir(parents=True)
    state = {c: dict(px=10000.0, sh=1_000_000) for c, *_ in STOCKS}
    for d in MONTHS:
        rows = []
        for code, name, mk in STOCKS:
            s = state[code]
            s["px"] *= 1 + rng.normal(0.0, 0.05)
            if code == "000040" and d == pd.Timestamp("2021-06-30"):      # 2:1 split: price halves, shares double
                s["px"] /= 2; s["sh"] *= 2
            if code == "000050" and d == pd.Timestamp("2021-03-31"):      # snapshot missing for this month
                continue
            if code == "000060" and d > pd.Timestamp("2021-12-31"):       # delisted
                continue
            px = int(s["px"])
            rows.append(f"{d:%Y%m%d},{code},{name},{mk},{px},0,0,{px},{px},{px},1000,{px*1000},{px*s['sh']},{s['sh']}")
        (snap / f"{d:%Y%m%d}.csv").write_text(HDR + "\n" + "\n".join(rows) + "\n", encoding="cp949")
    days = pd.bdate_range("2019-12-02", "2023-01-31")
    lvl = 2000 * np.exp(np.cumsum(rng.normal(0, 0.008, len(days))))
    (krx / "index_kospi.csv").write_text("일자,종가\n" + "\n".join(f"{d:%Y-%m-%d},{v:.2f}" for d, v in zip(days, lvl)),
                                        encoding="cp949")
    return pd.Series(lvl, index=days)


def write_raw(raw):
    q = pd.date_range("2018-03-31", "2022-12-31", freq="QE")
    fr = []
    for code, *_ in STOCKS:
        f = pd.DataFrame(dict(ticker=code, period_end=q, filing_date=q + pd.Timedelta(days=45)))
        for c in ["sales", "gross_profit", "op_income", "net_income", "cfo", "interest_expense"]:
            f[c] = rng.uniform(5, 10, len(q))
        for c in ["equity", "assets", "liabilities", "current_assets", "current_liabilities", "inventory", "cash", "debt"]:
            f[c] = rng.uniform(50, 100, len(q))
        fr.append(f)
    pd.concat(fr).to_parquet(raw / "fundamentals.parquet")
    mo = pd.date_range("2018-01-31", "2022-12-31", freq="ME")
    pd.concat([pd.DataFrame(dict(name=n, avail_date=mo + pd.Timedelta(days=5), value=1.0)) for n in MACRO]
              ).to_parquet(raw / "macro.parquet")


with tempfile.TemporaryDirectory() as d:
    krx, raw = Path(d) / "krx", Path(d) / "real"; raw.mkdir(); krx.mkdir()
    idx = write(krx); write_raw(raw)
    snaps = load_snapshots(krx / "snapshots")
    assert snaps["ticker"].str.len().eq(6).all() and snaps["date"].nunique() == len(MONTHS)
    pm = build_monthly(snaps)
    pm.to_parquet(raw / "prices_monthly.parquet"); load_index(krx).to_parquet(raw / "index.parquet")

    el = pm.drop_duplicates("ticker").set_index("ticker")["eligible"].to_dict()
    assert el["000010"] and el["000030"] and el["000080"]
    assert not el["000015"], "preferred share must be excluded"
    assert not el["000020"], "financial holding must be excluded"
    assert not el["000070"], "SPAC must be excluded"

    sp = pm[(pm.ticker == "000040") & (pm.date == "2021-06-30")].iloc[0]
    assert abs(sp.ret1) < 0.4, f"split month must not look like a -50% move, got {sp.ret1}"
    g = pm[pm.ticker == "000050"].sort_values("date")
    assert g.loc[g.date == "2021-04-30", "ret1"].isna().all(), "return across a missing snapshot must be NaN"
    assert g["seg"].nunique() == 2

    p = build_panel(raw, market="KOSPI", min_coverage=0.0)
    assert set(p.ticker) == {"000010", "000040", "000050", "000060", "000080"}, set(p.ticker)
    # benchmark = KOSPI index return from the last trading day of the month to the next month-end
    m_idx = idx.resample("ME").last()
    t = pd.Timestamp("2021-08-31")
    want = m_idx[pd.Timestamp("2021-09-30")] / m_idx[t] - 1
    got = p.loc[p.date == t, "mkt_next"].iloc[0]
    assert np.isclose(got, want, atol=1e-4), (got, want)   # index csv is rounded to 2 decimals
    assert "VOL_20D" not in p.columns and "RET_12M" in p.columns
    # 12M return needs 12 months of history: the first valid value appears 12 months after the first snapshot
    a = p[p.ticker == "000010"].set_index("date")["RET_12M"]
    assert a[:"2020-11-30"].isna().all() and a["2020-12-31":].notna().any()
    # KOSDAQ names appear only when no market filter is given (index for KOSDAQ missing -> dropped by benchmark merge)
    assert "000030" not in p.ticker.values
print("krx tests passed")

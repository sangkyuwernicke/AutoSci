"""Build the (date, ticker) factor panel from raw KOSPI/KOSDAQ files with look-ahead control.

Expected files in `raw_dir` (produce them with fetch_real_data.py or your own source):

prices.parquet        daily: date, ticker, close (split/dividend-adjusted), mcap (KRW), market
                      ("KOSPI"/"KOSDAQ"), eligible (bool; False for financials, SPACs and
                      administrative / investment-caution issues *on that date*)
fundamentals.parquet  one row per ticker x quarter: ticker, period_end, filing_date,
                      quarterly STAND-ALONE flows  sales, gross_profit, op_income, net_income, cfo,
                      interest_expense, depreciation (optional)
                      and period-end stocks  equity, assets, liabilities, current_assets,
                      current_liabilities, inventory, cash, debt
macro.parquet         long: name, avail_date, value  for the five MACRO series (CPI_YOY and
                      TERM_SPREAD already derived; avail_date = date the figure became public)
index.parquet         optional daily: date, market, close  (benchmark blend, weighted by market cap)
consensus.parquet     optional, POINT-IN-TIME analyst consensus (see prepare_consensus.py):
                      ticker, snapshot_date, target_year, metric ("ni" | "sales"), value (KRW)
                      -> enables FWD_PER, FWD_EPS_GROWTH, FWD_SALES_GROWTH, EST_REVISION_3M

Optional fundamentals columns: capex (stand-alone, positive = outflow) -> CAPEX_INTENSITY;
rd_annual / sales_annual (filled on annual-report rows only) -> RD_INTENSITY, RD_GROWTH.
Factors whose inputs are missing are simply left out of the returned panel.

Look-ahead rules: a fundamentals row is usable from `filing_date` on, never from `period_end`;
macro at month t uses only figures public by the end of month t-1.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from config import EXTENDED_FACTORS, MACRO

FLOWS = ["sales", "gross_profit", "op_income", "net_income", "cfo", "interest_expense", "depreciation", "capex"]
STOCKS = ["equity", "assets", "liabilities", "current_assets", "current_liabilities",
          "inventory", "cash", "debt"]
MAX_STALENESS_MONTHS = 18


def _fundamental_factors(f):
    f = f.sort_values(["ticker", "period_end"]).copy()
    if "depreciation" not in f:
        f["depreciation"] = 0.0
    flows = [c for c in FLOWS if c in f]
    g = f.groupby("ticker")
    ttm = g[flows].transform(lambda s: s.rolling(4, min_periods=4).sum()).add_suffix("_ttm")
    f = pd.concat([f, ttm], axis=1)
    for c, out in [("sales", "SALES_GROWTH"), ("op_income", "OP_GROWTH")]:
        prev = g[c].shift(4)
        f[out] = (f[c] - prev) / prev.abs().replace(0, np.nan)
    f["ROE"] = f.net_income_ttm / f.equity
    f["ROA"] = f.net_income_ttm / f.assets
    f["OPM"] = f.op_income_ttm / f.sales_ttm
    f["GPOA"] = f.gross_profit_ttm / f.assets
    f["DEBT_RATIO"] = f.liabilities / f.equity
    f["QUICK_RATIO"] = (f.current_assets - f.inventory) / f.current_liabilities
    f["ICR"] = f.op_income_ttm / f.interest_expense_ttm.abs().replace(0, np.nan)
    f["EBITDA_ttm"] = f.op_income_ttm + f.depreciation_ttm
    f["ASSET_GROWTH"] = f.assets / g["assets"].shift(4) - 1
    if "capex" in f:
        f["CAPEX_INTENSITY"] = f.capex_ttm.abs() / f.sales_ttm.replace(0, np.nan)
    return f


def _rd_factors(f):
    """R&D intensity / growth from annual-report rows (R&D is only reliably disclosed annually)."""
    a = f.loc[f["rd_annual"].notna() & f["sales_annual"].notna(), ["ticker", "filing_date", "rd_annual", "sales_annual"]]
    a = a.sort_values(["ticker", "filing_date"]).copy()
    a["RD_INTENSITY"] = a.rd_annual / a.sales_annual.replace(0, np.nan)
    prev = a.groupby("ticker")["rd_annual"].shift(1)
    a["RD_GROWTH"] = (a.rd_annual - prev) / prev.abs().replace(0, np.nan)
    return (a[["ticker", "filing_date", "RD_INTENSITY", "RD_GROWTH"]]
            .rename(columns={"filing_date": "rd_filed"}).sort_values("rd_filed"))


def _forward_factors(panel, cons_path, lag_days=0):
    """Forward-looking factors from point-in-time consensus. 12-month-forward estimate =
    (12-m)/12 * FY(t) + m/12 * FY(t+1) at month m, i.e. the calendar-year forecasts rolled forward.
    Snapshots are used only if dated <= t (minus `lag_days`) and no older than 45 days."""
    c = pd.read_parquet(cons_path)
    c["snapshot_date"] = pd.to_datetime(c["snapshot_date"]) + pd.Timedelta(days=lag_days)
    c["target_year"] = c["target_year"].astype("int64")
    c = c.drop_duplicates(["ticker", "snapshot_date", "target_year", "metric"], keep="last")
    t0 = panel["date"].min() + pd.offsets.MonthEnd(-3)
    grid = pd.date_range(t0, panel["date"].max(), freq="ME")
    tickers = panel["ticker"].unique()
    base = pd.MultiIndex.from_product([tickers, grid], names=["ticker", "d"]).to_frame(index=False)
    out = {}
    for metric in ("ni", "sales"):
        cm = c[c["metric"] == metric]
        if cm.empty:
            continue
        cm = cm.rename(columns={"value": "est"}).sort_values("snapshot_date")
        rows = []
        for off in (0, 1):                                   # FY(t) and FY(t+1)
            r = base.assign(target_year=(base["d"].dt.year + off).astype("int64")).sort_values("d")
            r = pd.merge_asof(r, cm[["ticker", "snapshot_date", "target_year", "est"]],
                              left_on="d", right_on="snapshot_date", by=["ticker", "target_year"],
                              tolerance=pd.Timedelta(days=45), direction="backward")
            rows.append(r[["ticker", "d", "target_year", "est"]].assign(off=off))
        est = pd.concat(rows)
        w = est.pivot_table(index=["ticker", "d"], columns="off", values="est", aggfunc="last")
        w.columns = ["y0", "y1"]
        w = w.reset_index()
        m = w["d"].dt.month
        w["fwd12"] = np.where(w.y1.isna(), w.y0, (12 - m) / 12 * w.y0 + m / 12 * w.y1)
        out[metric] = (w, est)

    if "ni" not in out and "sales" not in out:
        return panel
    p = panel
    if "ni" in out:
        p = p.merge(out["ni"][0][["ticker", "d", "fwd12"]].rename(columns={"d": "date", "fwd12": "fwd_ni"}),
                    on=["ticker", "date"], how="left")
        p["FWD_PER"] = p.mcap / p.fwd_ni
        p["FWD_EPS_GROWTH"] = (p.fwd_ni - p.net_income_ttm) / p.net_income_ttm.abs().replace(0, np.nan)
        # revision: estimate of the SAME fiscal year, now vs 3 months ago
        est = out["ni"][1].rename(columns={"d": "date", "est": "est_now"})
        now = p[["ticker", "date"]].assign(target_year=p["date"].dt.year.astype("int64")).merge(
            est[["ticker", "date", "target_year", "est_now"]], on=["ticker", "date", "target_year"], how="left")
        prev = p[["ticker", "date"]].assign(target_year=p["date"].dt.year.astype("int64"), date3=p["date"] + pd.offsets.MonthEnd(-3))
        prev = prev.merge(est.rename(columns={"date": "date3", "est_now": "est_prev"})[
            ["ticker", "date3", "target_year", "est_prev"]], on=["ticker", "date3", "target_year"], how="left")
        with np.errstate(divide="ignore", invalid="ignore"):
            p["EST_REVISION_3M"] = ((now["est_now"].to_numpy() - prev["est_prev"].to_numpy())
                                    / np.abs(prev["est_prev"].to_numpy()))
        p.loc[~np.isfinite(p["EST_REVISION_3M"]), "EST_REVISION_3M"] = np.nan
    if "sales" in out:
        sw = out["sales"][0][["ticker", "d", "fwd12"]].rename(columns={"d": "date", "fwd12": "fwd_sales"})
        p = p.merge(sw, on=["ticker", "date"], how="left")
        p["FWD_SALES_GROWTH"] = p.fwd_sales / p.sales_ttm.replace(0, np.nan) - 1
    return p


def build_panel(raw_dir, min_mcap_pct=0.0, consensus_lag_days=0):
    raw = Path(raw_dir)
    px = pd.read_parquet(raw / "prices.parquet")
    px["date"] = pd.to_datetime(px["date"])
    close = px.pivot_table(index="date", columns="ticker", values="close", aggfunc="last").sort_index()

    # ---- price-based block, on a month-end grid (labels = calendar month ends)
    m_close = close.resample("ME").last()
    vol20 = close.pct_change(fill_method=None).rolling(20, min_periods=15).std().resample("ME").last()
    dist52 = (close / close.rolling(252, min_periods=200).max() - 1).resample("ME").last()
    long = pd.DataFrame({
        "RET_1M": m_close.pct_change(1, fill_method=None).stack(),
        "RET_3M": m_close.pct_change(3, fill_method=None).stack(),
        "RET_12M": m_close.pct_change(12, fill_method=None).stack(),
        "VOL_20D": vol20.stack(),
        "RET_6M": m_close.pct_change(6, fill_method=None).stack(),
        "MOM_12_1": (m_close.shift(1) / m_close.shift(12) - 1).stack(),   # 12M return skipping the last month
        "DIST_52W_HIGH": dist52.stack(),
        "ret_next": (m_close.shift(-1) / m_close - 1).stack(),
    })
    long.index.names = ["date", "ticker"]
    last = (px.assign(date=px["date"] + pd.offsets.MonthEnd(0))
              .sort_values("date").groupby(["date", "ticker"])
              .agg(mcap=("mcap", "last"), market=("market", "last"), eligible=("eligible", "last")))
    panel = long.join(last, how="left").reset_index()
    panel = panel[panel["eligible"].fillna(False).astype(bool)]
    if min_mcap_pct > 0:                                     # liquidity / micro-cap screen, per month
        cut = panel.groupby("date")["mcap"].transform(lambda x: x.quantile(min_mcap_pct / 100))
        panel = panel[panel["mcap"] >= cut]

    # ---- benchmark return for t+1
    if (raw / "index.parquet").exists():
        ix = pd.read_parquet(raw / "index.parquet"); ix["date"] = pd.to_datetime(ix["date"])
        ic = ix.pivot_table(index="date", columns="market", values="close", aggfunc="last").resample("ME").last()
        ir = (ic.shift(-1) / ic - 1).stack().rename("mret").reset_index()
        ir.columns = ["date", "market", "mret"]
        cap = last.reset_index().groupby(["date", "market"])["mcap"].sum().rename("cap").reset_index()
        b = ir.merge(cap, on=["date", "market"]).dropna()
        bench = b.groupby("date").apply(lambda x: np.average(x.mret, weights=x.cap), include_groups=False)
        panel["mkt_next"] = panel["date"].map(bench)
    else:
        w = panel.dropna(subset=["ret_next", "mcap"])
        bench = w.groupby("date").apply(lambda x: np.average(x.ret_next, weights=x.mcap), include_groups=False)
        panel["mkt_next"] = panel["date"].map(bench)

    # ---- fundamentals as of filing date
    f = pd.read_parquet(raw / "fundamentals.parquet")
    f["period_end"] = pd.to_datetime(f["period_end"]); f["filing_date"] = pd.to_datetime(f["filing_date"])
    rd = _rd_factors(f) if {"rd_annual", "sales_annual"} <= set(f.columns) else None
    f = _fundamental_factors(f).sort_values("filing_date")
    keep = ["ticker", "filing_date", "period_end", "SALES_GROWTH", "OP_GROWTH", "ROE", "ROA", "OPM",
            "GPOA", "DEBT_RATIO", "QUICK_RATIO", "ICR", "ASSET_GROWTH", "net_income_ttm", "sales_ttm",
            "equity", "cfo_ttm", "EBITDA_ttm", "debt", "cash"]
    if "capex" in f:
        keep.append("CAPEX_INTENSITY")
    panel = pd.merge_asof(panel.sort_values("date"), f[keep], left_on="date", right_on="filing_date",
                          by="ticker", direction="backward")
    stale = panel["period_end"] < panel["date"] - pd.DateOffset(months=MAX_STALENESS_MONTHS)
    panel.loc[stale, keep[3:]] = np.nan
    panel["PER"] = panel.mcap / panel.net_income_ttm.replace(0, np.nan)
    panel["PBR"] = panel.mcap / panel.equity.replace(0, np.nan)
    panel["PCR"] = panel.mcap / panel.cfo_ttm.replace(0, np.nan)
    panel["EV_EBITDA"] = (panel.mcap + panel.debt - panel.cash) / panel.EBITDA_ttm.replace(0, np.nan)
    if rd is not None:
        panel = pd.merge_asof(panel.sort_values("date"), rd, left_on="date", right_on="rd_filed", by="ticker",
                              direction="backward", tolerance=pd.Timedelta(days=548))
        has_fin = panel["period_end"].notna()                # firms with statements but no R&D line: R&D = 0
        panel.loc[has_fin, ["RD_INTENSITY", "RD_GROWTH"]] = panel.loc[has_fin, ["RD_INTENSITY", "RD_GROWTH"]].fillna(0.0)
    if (raw / "consensus.parquet").exists():
        panel = _forward_factors(panel, raw / "consensus.parquet", consensus_lag_days)

    # ---- macro: only figures public by the end of the previous month
    mac = pd.read_parquet(raw / "macro.parquet"); mac["avail_date"] = pd.to_datetime(mac["avail_date"])
    grid = pd.DataFrame({"date": sorted(panel["date"].unique())})
    grid["asof"] = grid["date"] - pd.offsets.MonthEnd(1) + pd.Timedelta(hours=23, minutes=59)
    for name in MACRO:
        s = mac[mac["name"] == name].sort_values("avail_date")[["avail_date", "value"]]
        grid = pd.merge_asof(grid.sort_values("asof"), s, left_on="asof", right_on="avail_date",
                             direction="backward").rename(columns={"value": name}).drop(columns="avail_date")
    panel = panel.merge(grid.drop(columns="asof"), on="date", how="left")

    panel = panel.dropna(subset=["ret_next", "mkt_next"] + MACRO)
    feats = [c for c in EXTENDED_FACTORS if c in panel.columns]
    return panel[["date", "ticker"] + feats + MACRO + ["ret_next", "mkt_next"]].reset_index(drop=True)

"""Shared constants for the ML factor x macro excess-return experiment."""

BASE_FACTORS = [
    # Value
    "PER", "PBR", "PCR", "EV_EBITDA",
    # Profitability
    "ROE", "ROA", "OPM", "GPOA",
    # Growth
    "SALES_GROWTH", "OP_GROWTH",
    # Quality / stability
    "DEBT_RATIO", "QUICK_RATIO", "ICR",
    # Momentum / technical
    "RET_1M", "RET_3M", "RET_12M", "VOL_20D",
]
# Additional momentum / technical
MOMENTUM_EXTRA = ["RET_6M", "MOM_12_1", "DIST_52W_HIGH"]
# Reinvestment / future-growth proxies from filed statements
GROWTH_INVEST = ["RD_INTENSITY", "RD_GROWTH", "CAPEX_INTENSITY", "ASSET_GROWTH"]
# Analyst-consensus based (point-in-time consensus file required)
FORWARD_FACTORS = ["FWD_PER", "FWD_EPS_GROWTH", "FWD_SALES_GROWTH", "EST_REVISION_3M"]
EXTENDED_FACTORS = BASE_FACTORS + MOMENTUM_EXTRA + GROWTH_INVEST + FORWARD_FACTORS
FACTOR_SETS = {"base": BASE_FACTORS, "extended": EXTENDED_FACTORS}
FIRM_FACTORS = BASE_FACTORS          # default (the plan's original 17)

MACRO = ["BASE_RATE", "TERM_SPREAD", "CPI_YOY", "KRWUSD", "VKOSPI"]
ALL_FEATURES = FIRM_FACTORS + MACRO

# Value ratios are rank-transformed on their inverse (E/P, B/P, ...) so that
# loss-making firms (negative PER) sort to the bottom instead of the top.
INVERT_BEFORE_RANK = ["PER", "PBR", "PCR", "EV_EBITDA", "FWD_PER"]

# Macro variables used to define regimes for the SHAP analysis (H3).
REGIME_VARS = {"BASE_RATE": "rate", "TERM_SPREAD": "spread", "CPI_YOY": "inflation"}

MODELS = ["logit", "ridge", "dtree", "rf", "xgb", "lgbm", "catboost"]
TREE_MODELS = ["rf", "xgb", "lgbm", "catboost"]

# ECOS statistic codes (BoK). Verify against https://ecos.bok.or.kr before use.
ECOS_SERIES = {
    "BASE_RATE": dict(stat="722Y001", cycle="M", item="0101000"),
    "CPI_INDEX": dict(stat="901Y009", cycle="M", item="0"),
    "KRWUSD": dict(stat="731Y001", cycle="D", item="0000001"),
    "KTB10Y": dict(stat="817Y002", cycle="D", item="010210000"),
    # ECOS has no 2y KTB daily series under this table; 3y is used as proxy.
    "KTB3Y": dict(stat="817Y002", cycle="D", item="010200000"),
}

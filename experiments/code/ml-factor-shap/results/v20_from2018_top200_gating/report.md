# Experiment report
data=real trials=15 cost=0.002 top_q=200.0 (>=1: number of stocks) target=direction margin=0.0 quantile=None
primary benchmark = KOSPI200_EW_OFFICIAL (WinRate_vs_bm, Excess_mo [mean monthly excess] and t_excess are measured against it)

## Prediction + backtest (net of costs)
```
                  model                 fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Excess_mo  t_excess  Turnover
0              catboost            Firm-only      0.5307       0.5451  0.4771     0.4875     0.4594 0.0583  0.3616 -0.3704         0.5472     0.0013    0.4461    0.3707
1                  lgbm            Firm-only      0.5281       0.5436  0.4721     0.4869     0.4594 0.0556  0.3508 -0.3801         0.5660     0.0011    0.3711    0.3793
2                 logit            Firm-only      0.5249       0.5375  0.4717     0.4843     0.4594 0.0542  0.3458 -0.4202         0.5000     0.0009    0.3283    0.2957
3           macro_gated  Firm+Macro (gating)      0.5205       0.5370  0.4733     0.4841     0.4594 0.0727  0.4179 -0.3791         0.5377     0.0025    0.8986    0.3268
4                MARKET                    -         NaN          NaN     NaN        NaN        NaN 0.1012  0.4774 -0.3459         0.5377     0.0057    1.2550       NaN
5           EW_UNIVERSE                    -         NaN          NaN     NaN        NaN        NaN 0.0462  0.3141 -0.3892         0.5283     0.0003    0.1144       NaN
6     KOSPI200_OFFICIAL                    -         NaN          NaN     NaN        NaN        NaN 0.1223  0.5230 -0.3589         0.5755     0.0078    1.4154       NaN
7  KOSPI200_EW_OFFICIAL                    -         NaN          NaN     NaN        NaN        NaN 0.0422  0.2942 -0.4382         0.0000     0.0000       NaN       NaN
8        KOSPI200_PROXY                    -         NaN          NaN     NaN        NaN        NaN 0.1123  0.4963 -0.3425         0.5189     0.0070    1.3465       NaN
```

fset: Firm-only = firm characteristics only; Firm+Macro = firm characteristics and macro variables as direct inputs; Firm+Macro (gating) = macro variables only set the factor weights (stored as firm / full / gated in metrics.csv).

## Resolving power
106 test months x ~635 stocks, positive rate 0.46: the mean monthly AUC of a model with no skill has s.e. ~0.002; AUC gaps below ~0.006 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=gating factor_set=base sentiment=none market=KOSPI top_n_mcap=0

## H1: macro_gated vs firm-only models (paired by month)
```
  macro_gated_vs  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0          logit     auc   -0.00050 -0.12701  0.55041     0.86261       106    -0.00680     0.00727 0.58000 1.00000
1          logit  prec_k   -0.00028 -0.08079  0.53212     0.76894       106    -0.00684     0.00727 0.55540 1.00000
2           lgbm     auc   -0.00653 -1.44240  0.92392     0.91159       106    -0.01411     0.00154 0.94120 1.00000
3           lgbm  prec_k   -0.00288 -0.66520  0.74631     0.74235       106    -0.01061     0.00528 0.75540 1.00000
4       catboost     auc   -0.00803 -1.78263  0.96123     0.96467       106    -0.01518    -0.00015 0.97640 1.00000
5       catboost  prec_k   -0.00344 -0.80035  0.78734     0.74742       106    -0.01189     0.00509 0.78380 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b   diff   ci_lo  ci_hi  p_one_sided  n_months
0      lgbm  logit    0.3508    0.3458 0.0050 -0.0797 0.0987       0.4460       106
1  catboost  logit    0.3616    0.3458 0.0158 -0.0733 0.1090       0.3468       106
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
              mean_abs_shap
VOL_20D              0.0405
RET_3M               0.0326
RET_1M               0.0283
OP_GROWTH            0.0248
SALES_GROWTH         0.0242
ROE                  0.0228
OPM                  0.0176
RET_12M              0.0153
PCR                  0.0143
PBR                  0.0126

[BASE_RATE high vs low] rank corr=0.770, permutation p=0.0020, months high/low=50/56, sign flips=4/17
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D      0.0475   0.0342          1         4   -0.6519  -0.2412      False
RET_3M       0.0247   0.0409          2         1   -0.7699  -0.6790      False
OP_GROWTH    0.0195   0.0305          3         5    0.7902   0.6446      False
RET_1M       0.0184   0.0388          4         2   -0.7716  -0.7610      False
ROE          0.0183   0.0276          5         6    0.1107  -0.3878       True
OPM          0.0134   0.0223          6         8    0.7455   0.6121      False
PCR          0.0130   0.0161          7        11    0.9039   0.6281      False
PBR          0.0113   0.0143          8        12    0.7931   0.5032      False

[TERM_SPREAD high vs low] rank corr=0.953, permutation p=0.0020, months high/low=53/53, sign flips=2/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D         0.0409   0.0401          1         1   -0.3475  -0.4992      False
RET_3M          0.0359   0.0307          2         2   -0.6973  -0.7522      False
RET_1M          0.0333   0.0250          3         3   -0.7706  -0.7637      False
SALES_GROWTH    0.0320   0.0187          4         6    0.7118   0.7121      False
OP_GROWTH       0.0282   0.0224          5         4    0.7123   0.7057      False
ROE             0.0262   0.0202          6         5   -0.1359  -0.1956      False
OPM             0.0219   0.0143          7         7    0.7595   0.5668      False
RET_12M         0.0180   0.0138          8         8   -0.3481  -0.5268      False

[CPI_YOY high vs low] rank corr=0.900, permutation p=0.0020, months high/low=53/53, sign flips=3/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D         0.0418   0.0392          1         1   -0.5798  -0.2758      False
RET_3M          0.0275   0.0390          2         2   -0.7866  -0.6676      False
RET_1M          0.0197   0.0386          3         3   -0.7728  -0.7621      False
OP_GROWTH       0.0193   0.0313          4         5    0.7747   0.6591      False
ROE             0.0191   0.0273          5         6    0.0153  -0.3257       True
SALES_GROWTH    0.0141   0.0366          6         4    0.7454   0.7022      False
OPM             0.0132   0.0230          7         7    0.7171   0.6183      False
PCR             0.0131   0.0161          8        11    0.8983   0.6272      False

[Macro-Gated Mode] Factor weight time series -> gating_factor_weights.csv
Regime centroids (last test fold):
          BASE_RATE  TERM_SPREAD  CPI_YOY    KRWUSD  VKOSPI
regime_0     1.1620       0.4250   1.3906 1146.6183 17.8344
regime_1     3.0407       0.1474   3.3258 1352.8047 19.1116

Factor weights at first/last test month:
               PER     PBR    PCR  EV_EBITDA    ROE    ROA    OPM    GPOA  SALES_GROWTH  OP_GROWTH  DEBT_RATIO  QUICK_RATIO     ICR  RET_1M  RET_3M  RET_12M  VOL_20D
2017-12-31  0.0981 -0.0009 0.0298     0.0647 0.0878 0.0921 0.0959 -0.0479        0.0000     0.0000      0.0867      -0.0950  0.0920  0.1837 -0.0058   0.0581  -0.0996
2026-09-30 -0.0140  0.0702 0.0337     0.0010 0.0009 0.0547 0.0485  0.0012        0.0234     0.0194      0.0138       0.0266 -0.0041 -0.0277 -0.0375   0.0062   0.0109

```
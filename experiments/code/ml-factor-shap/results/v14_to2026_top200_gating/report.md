# Experiment report
data=real trials=15 cost=0.002 top_q=200.0 (>=1: number of stocks) target=direction margin=0.0 quantile=None
primary benchmark = KOSPI200_EW_OFFICIAL (WinRate_vs_bm, Excess_mo [mean monthly excess] and t_excess are measured against it)

## Prediction + backtest (net of costs)
```
                  model                 fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Excess_mo  t_excess  Turnover
0              catboost            Firm-only      0.5394       0.5570  0.4825     0.4917     0.4589 0.0806  0.4482 -0.2999         0.5366    -0.0005   -0.1339    0.3573
1                  lgbm            Firm-only      0.5344       0.5539  0.4775     0.4921     0.4589 0.0757  0.4278 -0.3022         0.5366    -0.0008   -0.2205    0.3748
2                 logit            Firm-only      0.5323       0.5504  0.4791     0.4926     0.4589 0.0898  0.4867 -0.2854         0.5000     0.0002    0.0570    0.2707
3           macro_gated  Firm+Macro (gating)      0.5270       0.5467  0.4947     0.4898     0.4589 0.1021  0.5230 -0.2799         0.5244     0.0013    0.3939    0.3138
4                MARKET                    -         NaN          NaN     NaN        NaN        NaN 0.1518  0.6071 -0.3459         0.5244     0.0065    1.1261       NaN
5           EW_UNIVERSE                    -         NaN          NaN     NaN        NaN        NaN 0.0669  0.3974 -0.2965         0.5000    -0.0016   -0.5969       NaN
6     KOSPI200_OFFICIAL                    -         NaN          NaN     NaN        NaN        NaN 0.1780  0.6490 -0.3589         0.5610     0.0090    1.2929       NaN
7  KOSPI200_EW_OFFICIAL                    -         NaN          NaN     NaN        NaN        NaN 0.0849  0.4578 -0.3155         0.0000     0.0000       NaN       NaN
8        KOSPI200_PROXY                    -         NaN          NaN     NaN        NaN        NaN 0.1640  0.6170 -0.3425         0.4878     0.0079    1.2064       NaN
```

fset: Firm-only = firm characteristics only; Firm+Macro = firm characteristics and macro variables as direct inputs; Firm+Macro (gating) = macro variables only set the factor weights (stored as firm / full / gated in metrics.csv).

## Resolving power
82 test months x ~648 stocks, positive rate 0.46: the mean monthly AUC of a model with no skill has s.e. ~0.003; AUC gaps below ~0.007 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=gating factor_set=base market=KOSPI top_n_mcap=0

## H1: macro_gated vs firm-only models (paired by month)
```
  macro_gated_vs  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0          logit     auc   -0.00371 -1.78388  0.96091     0.95080        82    -0.00822     0.00041 0.95820 1.00000
1          logit  prec_k   -0.00280 -1.04825  0.85118     0.89788        82    -0.00799     0.00232 0.85840 1.00000
2           lgbm     auc   -0.00720 -1.83849  0.96517     0.90500        82    -0.01438     0.00011 0.97260 1.00000
3           lgbm  prec_k   -0.00232 -0.56525  0.71327     0.69001        82    -0.01043     0.00579 0.71580 1.00000
4       catboost     auc   -0.01036 -2.83686  0.99712     0.99352        82    -0.01718    -0.00345 0.99880 1.00000
5       catboost  prec_k   -0.00195 -0.48425  0.68524     0.58455        82    -0.00976     0.00579 0.69180 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo  ci_hi  p_one_sided  n_months
0      lgbm  logit    0.4278    0.4867 -0.0589 -0.1489 0.0345       0.8880        82
1  catboost  logit    0.4482    0.4867 -0.0385 -0.1233 0.0443       0.8070        82
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
              mean_abs_shap
VOL_20D              0.0359
RET_3M               0.0255
RET_1M               0.0192
OP_GROWTH            0.0184
ROE                  0.0175
SALES_GROWTH         0.0111
OPM                  0.0109
PCR                  0.0102
RET_12M              0.0092
PBR                  0.0091

[BASE_RATE high vs low] rank corr=0.926, permutation p=0.0020, months high/low=33/49, sign flips=3/17
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D      0.0458   0.0288          1         1   -0.6927  -0.4621      False
RET_3M       0.0270   0.0247          2         2   -0.7524  -0.8503      False
RET_1M       0.0213   0.0180          3         4   -0.7858  -0.7817      False
OP_GROWTH    0.0189   0.0181          4         3    0.7845   0.7836      False
ROE          0.0179   0.0172          5         5    0.0264  -0.0829       True
OPM          0.0131   0.0093          6         7    0.7305   0.7458      False
PCR          0.0129   0.0084          7         9    0.8905   0.8881      False
PBR          0.0124   0.0068          8        10    0.8474   0.7801      False

[TERM_SPREAD high vs low] rank corr=0.953, permutation p=0.0020, months high/low=41/41, sign flips=2/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D         0.0312   0.0400          1         1   -0.4386  -0.6599      False
RET_3M          0.0234   0.0278          2         2   -0.8542  -0.7782      False
OP_GROWTH       0.0189   0.0179          3         4    0.7938   0.7763      False
RET_1M          0.0184   0.0202          4         3   -0.7908  -0.7770      False
ROE             0.0179   0.0171          5         5   -0.0540  -0.0174      False
OPM             0.0105   0.0111          6        10    0.7445   0.6964      False
SALES_GROWTH    0.0105   0.0118          7         6    0.7514   0.7464      False
PCR             0.0089   0.0115          8         7    0.8874   0.8846      False

[CPI_YOY high vs low] rank corr=0.931, permutation p=0.0020, months high/low=41/41, sign flips=2/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D         0.0394   0.0318          1         1   -0.6002  -0.4835      False
RET_3M          0.0269   0.0244          2         2   -0.7812  -0.8461      False
RET_1M          0.0181   0.0205          3         3   -0.7668  -0.7986      False
ROE             0.0180   0.0170          4         5   -0.0097  -0.0546      False
OP_GROWTH       0.0176   0.0192          5         4    0.7816   0.7886      False
RET_12M         0.0126   0.0060          6        10   -0.8030  -0.6647      False
PCR             0.0122   0.0082          7         8    0.9171   0.8617      False
SALES_GROWTH    0.0118   0.0105          8         6    0.7557   0.7493      False

[Macro-Gated Mode] Factor weight time series -> gating_factor_weights.csv
Regime centroids (last test fold):
          BASE_RATE  TERM_SPREAD  CPI_YOY    KRWUSD  VKOSPI
regime_0     1.3413       0.3528   1.4401 1139.4596 14.4488
regime_1     3.0407       0.1474   3.3258 1352.8047 19.1116
regime_2     0.6711       0.6226   1.2552 1166.2105 27.1000

Factor weights at first/last test month:
               PER    PBR    PCR  EV_EBITDA     ROE    ROA    OPM   GPOA  SALES_GROWTH  OP_GROWTH  DEBT_RATIO  QUICK_RATIO     ICR  RET_1M  RET_3M  RET_12M  VOL_20D
2019-12-31 -0.0112 0.0304 0.0356     0.0045 -0.0057 0.0849 0.0117 0.0193       -0.0129     0.0345     -0.0295       0.0008 -0.0347 -0.0269 -0.0593  -0.0496  -0.0162
2026-09-30 -0.0113 0.0719 0.0347     0.0021  0.0064 0.0441 0.0448 0.0003        0.0256     0.0171      0.0087       0.0232 -0.0029 -0.0269 -0.0347  -0.0001   0.0073

```
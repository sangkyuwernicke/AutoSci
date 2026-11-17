# Experiment report
data=real trials=15 cost=0.002 top_q=10.0 (>=1: number of stocks) target=direction margin=0.0 quantile=None
primary benchmark = KOSPI200_EW_OFFICIAL (WinRate_vs_bm, Excess_mo [mean monthly excess] and t_excess are measured against it)

## Prediction + backtest (net of costs)
```
                  model   fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Excess_mo  t_excess  Turnover
0              catboost   firm      0.5344       0.5509  0.4782     0.5056     0.4638 0.1721  0.6462 -0.3250         0.4722     0.0083    1.0985    0.6958
1                  lgbm   firm      0.5306       0.5497  0.4785     0.5042     0.4638 0.0577  0.3401 -0.3545         0.5000    -0.0015   -0.3182    0.7113
2                 logit   firm      0.5350       0.5499  0.4862     0.5167     0.4638 0.1446  0.5978 -0.2908         0.5000     0.0058    0.8745    0.5648
3           macro_gated  gated      0.5298       0.5458  0.5053     0.5097     0.4638 0.1552  0.6358 -0.2665         0.5000     0.0065    1.0158    0.6085
4                MARKET      -         NaN          NaN     NaN        NaN        NaN 0.1149  0.6105 -0.3459         0.5139     0.0021    0.5996       NaN
5           EW_UNIVERSE      -         NaN          NaN     NaN        NaN        NaN 0.0903  0.5184 -0.2968         0.5000     0.0001    0.0459       NaN
6     KOSPI200_OFFICIAL      -         NaN          NaN     NaN        NaN        NaN 0.1283  0.6487 -0.3589         0.5556     0.0032    0.7726       NaN
7  KOSPI200_EW_OFFICIAL      -         NaN          NaN     NaN        NaN        NaN 0.0904  0.5300 -0.3155         0.0000     0.0000       NaN       NaN
8        KOSPI200_PROXY      -         NaN          NaN     NaN        NaN        NaN 0.1229  0.6172 -0.3381         0.4861     0.0029    0.6941       NaN
```

## Resolving power
72 test months x ~647 stocks, positive rate 0.46: the mean monthly AUC of a model with no skill has s.e. ~0.003; AUC gaps below ~0.008 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=gating factor_set=base market=KOSPI top_n_mcap=0

## H1: macro_gated vs firm-only models (paired by month)
```
  macro_gated_vs  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0          logit     auc   -0.00410 -1.60200  0.94320     0.93298        72    -0.00856     0.00025 0.96940 1.00000
1          logit  prec_k   -0.00694 -0.42167  0.66273     0.71421        72    -0.03750     0.02361 0.67780 1.00000
2           lgbm     auc   -0.00388 -0.92085  0.81988     0.75144        72    -0.01220     0.00426 0.81940 1.00000
3           lgbm  prec_k    0.00556  0.27690  0.39133     0.56191        72    -0.03194     0.04583 0.40180 1.00000
4       catboost     auc   -0.00510 -1.16428  0.87590     0.75774        72    -0.01309     0.00268 0.90300 1.00000
5       catboost  prec_k    0.00417  0.17589  0.43044     0.45867        72    -0.04306     0.04861 0.42100 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo  ci_hi  p_one_sided  n_months
0      lgbm  logit    0.3401    0.5978 -0.2578 -0.6229 0.0813       0.9280        72
1  catboost  logit    0.6462    0.5978  0.0484 -0.3561 0.4204       0.4060        72
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
              mean_abs_shap
VOL_20D              0.0336
RET_3M               0.0293
OP_GROWTH            0.0223
RET_1M               0.0211
ROE                  0.0192
OPM                  0.0164
RET_12M              0.0152
SALES_GROWTH         0.0136
PCR                  0.0126
PBR                  0.0104

[BASE_RATE high vs low] rank corr=0.929, permutation p=0.0020, months high/low=31/41, sign flips=3/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D         0.0414   0.0273          1         2   -0.5320  -0.3920      False
RET_3M          0.0302   0.0288          2         1   -0.7077  -0.7760      False
OP_GROWTH       0.0217   0.0227          3         3    0.7454   0.7086      False
RET_1M          0.0213   0.0211          4         4   -0.7810  -0.7283      False
ROE             0.0200   0.0186          5         5    0.0147  -0.0690       True
OPM             0.0155   0.0171          6         6    0.5623   0.6147      False
SALES_GROWTH    0.0134   0.0139          7         8    0.7288   0.7432      False
RET_12M         0.0133   0.0166          8         7   -0.7155  -0.7096      False

[TERM_SPREAD high vs low] rank corr=0.961, permutation p=0.0359, months high/low=36/36, sign flips=2/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M          0.0263   0.0325          1         2   -0.7837  -0.7207      False
VOL_20D         0.0263   0.0404          2         1   -0.3576  -0.5327      False
OP_GROWTH       0.0210   0.0236          3         3    0.7213   0.7325      False
RET_1M          0.0190   0.0234          4         4   -0.7315  -0.7767      False
ROE             0.0174   0.0209          5         5   -0.0217  -0.0361      False
OPM             0.0152   0.0177          6         6    0.6213   0.5655      False
RET_12M         0.0140   0.0164          7         7   -0.6790  -0.7364      False
SALES_GROWTH    0.0127   0.0146          8         9    0.7382   0.7383      False

[CPI_YOY high vs low] rank corr=0.924, permutation p=0.0020, months high/low=36/36, sign flips=3/17
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D      0.0414   0.0253          1         1   -0.5305  -0.3607      False
RET_3M       0.0372   0.0216          2         2   -0.7201  -0.8159      False
OP_GROWTH    0.0287   0.0158          3         3    0.7175   0.7499      False
RET_1M       0.0270   0.0154          4         4   -0.7586  -0.7733      False
ROE          0.0245   0.0139          5         5   -0.1273   0.0268       True
OPM          0.0243   0.0086          6         7    0.5775   0.6581      False
RET_12M      0.0241   0.0063          7         8   -0.7711  -0.6050      False
PCR          0.0197   0.0054          8         9    0.8771   0.8568      False

[Macro-Gated Mode] Factor weight time series -> gating_factor_weights.csv
Regime centroids (last test fold):
          BASE_RATE  TERM_SPREAD  CPI_YOY    KRWUSD  VKOSPI
regime_0     1.1620       0.4250   1.3906 1146.6183 17.8344
regime_1     3.1774       0.0900   3.8698 1328.8161 17.8919

Factor weights at first/last test month:
               PER    PBR    PCR  EV_EBITDA    ROE    ROA    OPM    GPOA  SALES_GROWTH  OP_GROWTH  DEBT_RATIO  QUICK_RATIO     ICR  RET_1M  RET_3M  RET_12M  VOL_20D
2019-12-31 -0.0348 0.0418 0.0200     0.0102 0.0076 0.0331 0.0229  0.0295        0.0153     0.0198     -0.0098       0.0074 -0.0237 -0.0263 -0.0408  -0.0141  -0.0128
2025-11-30  0.0074 0.0381 0.0245    -0.0018 0.0089 0.0447 0.0533 -0.0045        0.0014     0.0358      0.0196       0.0168  0.0087 -0.0247 -0.0507   0.0337   0.0201

```
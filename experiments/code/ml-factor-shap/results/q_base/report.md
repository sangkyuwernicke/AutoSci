# Experiment report
data=real trials=15 cost=0.002 top_q=0.2 margin=0.0 quantile=None

## Prediction + backtest (net of costs)
```
          model  fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Turnover
0      catboost  firm      0.4957       0.4991  0.4516     0.4523     0.4548 0.2774  1.1925 -0.2049         0.5000    0.5630
1      catboost  full      0.4911       0.4882  0.4489     0.4294     0.4548 0.0811  0.4805 -0.2271         0.3611    0.4916
2         dtree  firm      0.4966       0.4945  0.4555     0.4527     0.4548 0.2086  0.9469 -0.1640         0.4722    0.2514
3         dtree  full      0.4977       0.4939  0.4540     0.4661     0.4548 0.2748  1.1136 -0.2052         0.5278    0.3110
4          lgbm  firm      0.4768       0.4808  0.4461     0.4610     0.4548 0.2744  1.1722 -0.1663         0.4444    0.4543
5          lgbm  full      0.4674       0.4853  0.4293     0.4576     0.4548 0.2322  1.0504 -0.1747         0.4722    0.4425
6         logit  firm      0.4923       0.4901  0.4582     0.4636     0.4548 0.2137  0.9109 -0.2107         0.4167    0.3594
7         logit  full      0.4852       0.4834  0.4488     0.4661     0.4548 0.2571  1.0699 -0.2060         0.5556    0.2810
8            rf  firm      0.4880       0.4784  0.4559     0.4307     0.4548 0.1791  0.8651 -0.1771         0.3333    0.3109
9            rf  full      0.4894       0.4847  0.4582     0.4509     0.4548 0.2137  1.0354 -0.1623         0.4167    0.3600
10        ridge  firm      0.4939       0.4911  0.4467     0.4521     0.4548 0.2264  0.9392 -0.2107         0.4444    0.3087
11        ridge  full      0.4665       0.4912  0.4290     0.4521     0.4548 0.2264  0.9392 -0.2107         0.4444    0.3087
12          xgb  firm      0.5027       0.4970  0.4571     0.4555     0.4548 0.2236  1.0411 -0.1808         0.4444    0.5153
13          xgb  full      0.4888       0.4951  0.4446     0.4560     0.4548 0.2063  0.9468 -0.1997         0.4722    0.4673
14       MARKET     -         NaN          NaN     NaN        NaN        NaN 0.2352  1.1489 -0.1424            NaN       NaN
15  EW_UNIVERSE     -         NaN          NaN     NaN        NaN        NaN 0.2813  1.3639 -0.1536         0.5833       NaN
```

## H1: full (firm+macro) minus firm-only, paired by month
```
       model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months
0      logit     auc   -0.00673 -0.71802  0.76124     0.78362        36
1      logit  prec_k    0.00251  0.12559  0.45039     0.22215        36
2      ridge     auc    0.00009  1.47200  0.07498     0.05793        36
3      ridge  prec_k    0.00000      NaN      NaN         NaN        36
4      dtree     auc   -0.00066 -0.04400  0.51742     0.52278        36
5      dtree  prec_k    0.01343  0.57419  0.28476     0.27723        36
6         rf     auc    0.00624  1.18794  0.12143     0.13623        36
7         rf  prec_k    0.02024  1.60596  0.05863     0.04196        36
8        xgb     auc   -0.00188 -0.23268  0.59132     0.54632        36
9        xgb  prec_k    0.00050  0.02627  0.48960     0.48786        36
10      lgbm     auc    0.00455  0.57805  0.28346     0.38700        36
11      lgbm  prec_k   -0.00342 -0.17277  0.56809     0.40465        36
12  catboost     auc   -0.01091 -0.95019  0.82573     0.84629        36
13  catboost  prec_k   -0.02285 -1.08448  0.85722     0.85785        36
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo   ci_hi  p_one_sided  n_months
0        rf  logit    1.0354    1.0699 -0.0345 -0.5262  0.3869       0.5362        36
1       xgb  logit    0.9468    1.0699 -0.1231 -0.6466  0.3799       0.6790        36
2      lgbm  logit    1.0504    1.0699 -0.0195 -0.4207  0.3147       0.5348        36
3  catboost  logit    0.4805    1.0699 -0.5895 -1.2944 -0.1158       0.9946        36
```

## H3: SHAP
```
Global mean|SHAP| (top 10):
            mean_abs_shap
RET_3M             0.1258
VKOSPI             0.0979
DEBT_RATIO         0.0911
PCR                0.0845
BASE_RATE          0.0822
PER                0.0696
KRWUSD             0.0685
OP_GROWTH          0.0655
GPOA               0.0654
CPI_YOY            0.0618

[BASE_RATE high vs low] rank corr=0.597, permutation p=0.0020, months high/low=21/15, sign flips=6/16
             imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M         0.1079   0.1494          1         1   -0.9303  -0.9258      False
PCR            0.0805   0.0913          2         4    0.6431   0.5166      False
DEBT_RATIO     0.0733   0.1148          3         2   -0.0168   0.2481       True
GPOA           0.0637   0.0705          4         7   -0.5090  -0.0369      False
OP_GROWTH      0.0614   0.0726          5         5   -0.6372  -0.4281      False
RET_12M        0.0589   0.0599          6        13   -0.7128  -0.2297      False
OPM            0.0532   0.0661          7        10   -0.3748   0.1025       True
QUICK_RATIO    0.0521   0.0653          8        11    0.7318   0.3151      False

[TERM_SPREAD high vs low] rank corr=0.712, permutation p=0.0020, months high/low=18/18, sign flips=5/16
            imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M        0.1381   0.1122          1         1   -0.9238  -0.9271      False
DEBT_RATIO    0.1028   0.0785          2         3    0.1949  -0.0107       True
PCR           0.0854   0.0846          3         2    0.5342   0.6268      False
PER           0.0827   0.0553          4         8   -0.4534  -0.5659      False
OP_GROWTH     0.0674   0.0648          5         5   -0.4416  -0.6501      False
OPM           0.0658   0.0514          6         9   -0.0657  -0.2660      False
GPOA          0.0643   0.0688          7         4   -0.0733  -0.5352      False
ROE           0.0626   0.0270          8        15    0.5821  -0.0450       True

[CPI_YOY high vs low] rank corr=0.629, permutation p=0.0020, months high/low=18/18, sign flips=5/16
             imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M         0.1148   0.1355          1         1   -0.9235  -0.9248      False
PCR            0.0868   0.0831          2         3    0.6215   0.5373      False
DEBT_RATIO     0.0814   0.0998          3         2    0.0064   0.1821      False
GPOA           0.0731   0.0600          4         8   -0.5535  -0.0457      False
OP_GROWTH      0.0683   0.0638          5         6   -0.6755  -0.4160      False
RET_12M        0.0638   0.0548          6        13   -0.6756  -0.3230      False
QUICK_RATIO    0.0604   0.0548          7        12    0.7086   0.3619      False
PER            0.0586   0.0794          8         4   -0.5761  -0.4370      False

Top macro x firm interactions (mean|phi_ij|*2):
                          value
TERM_SPREAD RET_3M       0.0266
VKOSPI      DEBT_RATIO   0.0210
CPI_YOY     RET_12M      0.0206
VKOSPI      OPM          0.0186
CPI_YOY     RET_3M       0.0173
TERM_SPREAD SALES_GROWTH 0.0172
CPI_YOY     ROE          0.0166
TERM_SPREAD PCR          0.0162

```
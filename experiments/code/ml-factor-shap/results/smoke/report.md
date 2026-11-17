# Experiment report
data=synthetic trials=15 cost=0.002 top_q=0.2 margin=0.0 quantile=None

## Prediction + backtest (net of costs)
```
          model  fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Turnover
0      catboost  firm      0.5856       0.5900  0.5796     0.6181     0.5022 0.4275  2.9416 -0.0474         0.9444    0.3343
1      catboost  full      0.5991       0.5982  0.5897     0.6222     0.5022 0.3798  2.6730 -0.0407         0.9167    0.4243
2         dtree  firm      0.5625       0.5605  0.5488     0.5847     0.5022 0.2784  1.9528 -0.1032         0.7222    0.4886
3         dtree  full      0.5589       0.5576  0.5467     0.5847     0.5022 0.2784  1.9528 -0.1032         0.7222    0.4886
4          lgbm  firm      0.5923       0.5936  0.5826     0.6097     0.5022 0.4151  2.8632 -0.0406         0.9722    0.3529
5          lgbm  full      0.5928       0.5943  0.5846     0.6167     0.5022 0.3997  2.7446 -0.0561         0.8889    0.3700
6         logit  firm      0.5869       0.5942  0.5731     0.6028     0.5022 0.3664  2.7477 -0.0560         0.8611    0.3014
7         logit  full      0.5874       0.5930  0.5734     0.6056     0.5022 0.3705  2.7216 -0.0560         0.8889    0.3029
8            rf  firm      0.5942       0.5954  0.5859     0.6097     0.5022 0.4109  2.9108 -0.0468         0.9444    0.3129
9            rf  full      0.5919       0.5945  0.5860     0.6028     0.5022 0.3837  2.6960 -0.0444         0.8889    0.3300
10        ridge  firm      0.5850       0.5941  0.5712     0.6056     0.5022 0.3680  2.7250 -0.0593         0.8333    0.3086
11        ridge  full      0.5858       0.5940  0.5720     0.6111     0.5022 0.3806  2.6997 -0.0593         0.8333    0.2943
12          xgb  firm      0.5819       0.5832  0.5760     0.6111     0.5022 0.3759  2.6764 -0.0641         0.8333    0.4043
13          xgb  full      0.5835       0.5868  0.5728     0.6056     0.5022 0.3662  2.6752 -0.0701         0.8333    0.4414
14       MARKET     -         NaN          NaN     NaN        NaN        NaN 0.1382  1.1598 -0.1121            NaN       NaN
15  EW_UNIVERSE     -         NaN          NaN     NaN        NaN        NaN 0.1382  1.1598 -0.1121         0.2500       NaN
```

## H1: full (firm+macro) minus firm-only, paired by month
```
       model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months
0      logit     auc   -0.00125 -1.24251  0.88885     0.85432        36
1      logit  prec_k    0.00278  0.62710  0.26733     0.28488        36
2      ridge     auc   -0.00016 -0.38156  0.64745     0.60326        36
3      ridge  prec_k    0.00556  2.09165  0.02190     0.03166        36
4      dtree     auc   -0.00298 -1.44006  0.92063     0.96835        36
5      dtree  prec_k    0.00000      NaN      NaN         NaN        36
6         rf     auc   -0.00089 -0.54511  0.70543     0.64238        36
7         rf  prec_k   -0.00694 -0.84173  0.79717     0.83721        36
8        xgb     auc    0.00354  1.36470  0.09053     0.10723        36
9        xgb  prec_k   -0.00556 -0.62710  0.73267     0.41504        36
10      lgbm     auc    0.00077  0.54353  0.29511     0.32433        36
11      lgbm  prec_k    0.00694  0.89555  0.18830     0.22932        36
12  catboost     auc    0.00818  2.29572  0.01390     0.01358        36
13  catboost  prec_k    0.00417  0.38592  0.35095     0.35812        36
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo  ci_hi  p_one_sided  n_months
0        rf  logit    2.6960    2.7216 -0.0255 -0.4759 0.4716       0.5252        36
1       xgb  logit    2.6752    2.7216 -0.0464 -0.6049 0.6355       0.5218        36
2      lgbm  logit    2.7446    2.7216  0.0231 -0.4463 0.5596       0.4572        36
3  catboost  logit    2.6730    2.7216 -0.0485 -0.6964 0.5972       0.5470        36
```

## H3: SHAP
```
Global mean|SHAP| (top 10):
              mean_abs_shap
PCR                  0.0751
OPM                  0.0690
SALES_GROWTH         0.0612
EV_EBITDA            0.0568
QUICK_RATIO          0.0520
ROE                  0.0514
RET_12M              0.0494
ROA                  0.0467
PBR                  0.0367
OP_GROWTH            0.0365

[BASE_RATE high vs low] rank corr=0.914, permutation p=0.0020, months high/low=21/15, sign flips=0/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
OPM             0.0787   0.0553          1         5    0.8805   0.9277      False
PCR             0.0652   0.0890          2         1    0.8590   0.9114      False
SALES_GROWTH    0.0578   0.0661          3         2    0.9534   0.9540      False
EV_EBITDA       0.0550   0.0594          4         3    0.7974   0.8397      False
RET_12M         0.0530   0.0443          5         8    0.8239   0.8434      False
QUICK_RATIO     0.0498   0.0551          6         6    0.9482   0.9135      False
ROE             0.0471   0.0574          7         4    0.9076   0.9101      False
ROA             0.0465   0.0469          8         7    0.7008   0.6606      False

[TERM_SPREAD high vs low] rank corr=0.914, permutation p=0.0020, months high/low=18/18, sign flips=0/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
PCR             0.0877   0.0626          1         2    0.9091   0.8580      False
SALES_GROWTH    0.0664   0.0561          2         3    0.9550   0.9541      False
EV_EBITDA       0.0623   0.0513          3         5    0.8198   0.8150      False
OPM             0.0588   0.0791          4         1    0.9226   0.8690      False
ROE             0.0550   0.0478          5         7    0.9092   0.9066      False
QUICK_RATIO     0.0542   0.0498          6         6    0.9242   0.9455      False
ROA             0.0472   0.0462          7         8    0.6772   0.6911      False
RET_12M         0.0437   0.0551          8         4    0.8332   0.8277      False

[CPI_YOY high vs low] rank corr=0.900, permutation p=0.0020, months high/low=18/18, sign flips=0/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
OPM             0.0811   0.0569          1         4    0.8704   0.9326      False
PCR             0.0601   0.0902          2         1    0.8586   0.9172      False
RET_12M         0.0564   0.0424          3         8    0.8277   0.8303      False
SALES_GROWTH    0.0556   0.0669          4         2    0.9531   0.9566      False
EV_EBITDA       0.0507   0.0630          5         3    0.8108   0.8243      False
QUICK_RATIO     0.0495   0.0545          6         6    0.9478   0.9212      False
ROE             0.0470   0.0558          7         5    0.9066   0.9096      False
ROA             0.0457   0.0476          8         7    0.6866   0.6812      False

Top macro x firm interactions (mean|phi_ij|*2):
                         value
VKOSPI      ROA         0.0039
CPI_YOY     ICR         0.0038
BASE_RATE   PCR         0.0032
TERM_SPREAD RET_12M     0.0031
CPI_YOY     QUICK_RATIO 0.0029
BASE_RATE   RET_12M     0.0029
KRWUSD      PCR         0.0026
VKOSPI      RET_3M      0.0026

```
# Firm-factor ML x Macro x News sentiment (KR-FinBert-SC)

KOSPI top-100 by market cap, 36 test months (2022-12~2025-11), label = next-month direction, portfolio = top 20% by predicted P(up), equal weight, cost 0.20% x sum|dw|; Sharpe = monthly mean/std x sqrt(12), rf = 0. Not the original design (whole KOSPI ~650 stocks, hold 200 vs KOSPI200 EW): the universe here is the ~91 largest stocks and the book is the top 20%. Index rows are net of nothing (price indices); model rows are net of cost.

## Panel A. Out-of-sample, 2x2 design per model

| Model                                    | AUC Firm   | AUC Firm+Macro   | AUC Firm+Sent   | AUC Firm+Macro+Sent   |   Sharpe Firm |   Sharpe Firm+Macro |   Sharpe Firm+Sent |   Sharpe Firm+Macro+Sent |
|:-----------------------------------------|:-----------|:-----------------|:----------------|:----------------------|--------------:|--------------------:|-------------------:|-------------------------:|
| logit                                    | 0.506      | 0.506            | 0.505           | 0.505                 |         0.505 |               0.505 |              0.464 |                    0.464 |
| ridge                                    | 0.515      | 0.515            | 0.513           | 0.513                 |         0.415 |               0.415 |              0.553 |                    0.575 |
| dtree                                    | 0.501      | 0.501            | 0.511           | 0.501                 |         0.698 |               0.736 |              1.023 |                    0.736 |
| rf                                       | 0.509      | 0.509            | 0.508           | 0.511                 |         0.64  |               0.45  |              0.759 |                    0.724 |
| xgb                                      | 0.497      | 0.479            | 0.498           | 0.484                 |         0.705 |               0.516 |              0.811 |                    0.282 |
| lgbm                                     | 0.513      | 0.506            | 0.501           | 0.505                 |         0.718 |               0.673 |              0.585 |                    0.757 |
| catboost                                 | 0.501      | 0.503            | 0.501           | 0.492                 |         0.776 |               0.902 |              0.588 |                    0.92  |
| Model mean                               | 0.506      | 0.503            | 0.505           | 0.502                 |         0.637 |               0.599 |              0.683 |                    0.637 |
| EW of test universe (no model, no cost)  | -          | -                | -               | -                     |         1.079 |               1.079 |              1.079 |                    1.079 |
| KOSPI200 EW official (primary benchmark) | -          | -                | -               | -                     |         1.084 |               1.084 |              1.084 |                    1.084 |
| KOSPI200 cap-weighted official           | -          | -                | -               | -                     |         1.224 |               1.224 |              1.224 |                    1.224 |

### Pooled effects (models averaged; CI = circular block bootstrap of the monthly AUC difference)

| Effect                             |   mean dAUC |   CI lo |   CI hi |   p (one-sided) |   mean dSharpe |   n_months |
|:-----------------------------------|------------:|--------:|--------:|----------------:|---------------:|-----------:|
| Macro effect (Firm+Macro - Firm)   |     -0.0036 | -0.0111 |  0.0039 |          0.8238 |        -0.0418 |         36 |
| Sentiment effect (+FinBert - none) |     -0.0010 | -0.0058 |  0.0041 |          0.6470 |         0.0419 |         36 |

## Panel B. Single-factor rank IC of the sentiment factors, mean IC (Newey-West t)

raw = as is; resid = after removing RET_1M, RET_3M, VOL_20D, market cap month by month.

| Factor        |   avg N (top100) | IC raw (top100)   | IC resid (top100)   |   avg N (top200) | IC raw (top200)   | IC resid (top200)   |
|:--------------|-----------------:|:------------------|:--------------------|-----------------:|:------------------|:--------------------|
| SENT_MEAN_1W  |             30.7 | -0.022 (-1.4)     | +0.019 (+1.4)       |             41.3 | -0.031 (-2.0)     | -0.000 (-0.0)       |
| SENT_MEAN_1M  |             63   | -0.023 (-1.5)     | -0.009 (-0.6)       |             96.6 | -0.007 (-0.7)     | +0.006 (+0.6)       |
| SENT_MEAN_3M  |             82.4 | -0.025 (-1.7)     | -0.014 (-1.1)       |            141.2 | -0.016 (-1.6)     | -0.007 (-0.8)       |
| SENT_CHG      |             24.1 | -0.032 (-1.7)     | -0.017 (-1.0)       |             29.8 | -0.027 (-1.6)     | -0.011 (-0.7)       |
| SENT_STD_1M   |             27.3 | -0.036 (-2.2)     | -0.033 (-2.2)       |             33.2 | -0.028 (-1.5)     | -0.026 (-1.5)       |
| NEWS_COUNT_1M |             90.4 | +0.016 (+1.3)     | +0.017 (+1.5)       |            179.1 | +0.009 (+1.0)     | +0.003 (+0.3)       |

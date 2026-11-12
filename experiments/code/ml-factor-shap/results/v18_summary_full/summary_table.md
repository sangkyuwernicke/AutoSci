# Firm-factor ML x Macro x News sentiment (KR-FinBert-SC)

Models: logit, lgbm, catboost. 646 stocks per month (median), 72 test months (2019-12~2025-11), label = next-month direction, portfolio = top 200 stocks by predicted P(up), equal weight, cost 0.20% x sum|dw|; Sharpe = monthly mean/std x sqrt(12), rf = 0. Index rows are price indices without costs; model rows are net of cost.

## Panel A. Out-of-sample, 2x2 design per model

| Model                                    | AUC Firm   | AUC Firm+Macro   | AUC Firm+Sent   | AUC Firm+Macro+Sent   |   Sharpe Firm |   Sharpe Firm+Macro |   Sharpe Firm+Sent |   Sharpe Firm+Macro+Sent |
|:-----------------------------------------|:-----------|:-----------------|:----------------|:----------------------|--------------:|--------------------:|-------------------:|-------------------------:|
| logit                                    | 0.550      | 0.550            | 0.549           | 0.549                 |         0.57  |               0.573 |              0.597 |                    0.593 |
| lgbm                                     | 0.552      | 0.537            | 0.547           | 0.542                 |         0.527 |               0.448 |              0.594 |                    0.489 |
| catboost                                 | 0.553      | 0.550            | 0.549           | 0.552                 |         0.536 |               0.476 |              0.542 |                    0.568 |
| Model mean                               | 0.552      | 0.545            | 0.548           | 0.547                 |         0.544 |               0.499 |              0.578 |                    0.55  |
| EW of test universe (no model, no cost)  | -          | -                | -               | -                     |         0.519 |               0.519 |              0.519 |                    0.519 |
| KOSPI200 EW official (primary benchmark) | -          | -                | -               | -                     |         0.53  |               0.53  |              0.53  |                    0.53  |
| KOSPI200 cap-weighted official           | -          | -                | -               | -                     |         0.649 |               0.649 |              0.649 |                    0.649 |

### Pooled effects (models averaged; CI = circular block bootstrap of the monthly AUC difference)

| Effect                             |   mean dAUC |   CI lo |   CI hi |   p (one-sided) |   mean dSharpe |   n_months |
|:-----------------------------------|------------:|--------:|--------:|----------------:|---------------:|-----------:|
| Macro effect (Firm+Macro - Firm)   |     -0.0037 | -0.0089 |  0.0013 |          0.9268 |        -0.0366 |         72 |
| Sentiment effect (+FinBert - none) |     -0.0006 | -0.0031 |  0.0018 |          0.6896 |         0.0421 |         72 |

## Panel B. Single-factor rank IC of the sentiment factors, mean IC (Newey-West t)

raw = as is; resid = after removing RET_1M, RET_3M, VOL_20D, market cap month by month.

| Factor        |   avg N (whole KOSPI) | IC raw (whole KOSPI)   | IC resid (whole KOSPI)   |
|:--------------|----------------------:|:-----------------------|:-------------------------|
| SENT_MEAN_1W  |                  58.7 | -0.016 (-1.1)          | +0.003 (+0.2)            |
| SENT_MEAN_1M  |                 153.3 | +0.004 (+0.4)          | +0.015 (+1.6)            |
| SENT_MEAN_3M  |                 260   | +0.004 (+0.5)          | +0.011 (+1.6)            |
| SENT_CHG      |                  37.1 | -0.017 (-1.0)          | -0.010 (-0.6)            |
| SENT_STD_1M   |                  39.9 | -0.011 (-0.6)          | -0.014 (-0.9)            |
| NEWS_COUNT_1M |                 620.5 | -0.005 (-0.6)          | +0.006 (+1.0)            |

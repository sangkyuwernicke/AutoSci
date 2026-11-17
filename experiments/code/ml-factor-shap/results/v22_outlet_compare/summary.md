# Outlet comparison (KR-FinBert-SC)

## Coverage by year (ticker-days)
outlet  pooled  매일경제   서울경제   한국경제
year                              
2015     15479  4234   6075  10016
2016     16206  5870   7003   9102
2017     19549  6848  10793   9792
2018     48046  7215  35882  21889
2019     40364  6156  26038  23760
2020     20910  6097   7145  13024
2021     14894  5454   7848   6975
2022     15496  5406   8447   7038
2023     14237  6057   6843   6854
2024     13926  6304   5951   6923
2025     14197  5473   6600   7343

## Ticker-day score distribution
        ticker_days  mean   std    q10   q50   q90  share_pos  share_neg  articles_per_ticker_day
매일경제      65114.000 0.169 0.704 -0.999 0.000 1.000      0.398      0.217                    1.301
서울경제     128625.000 0.428 0.679 -0.956 0.915 1.000      0.581      0.134                    1.473
한국경제     122716.000 0.327 0.723 -0.994 0.500 1.000      0.533      0.193                    1.414
pooled   233304.000 0.337 0.679 -0.962 0.461 1.000      0.525      0.163                    1.919

## Pairwise agreement on shared (ticker, date)
   a    b  n_shared  pearson  spearman  sign_agree
매일경제 서울경제     26240    0.495     0.508       0.769
매일경제 한국경제     26159    0.473     0.478       0.728
서울경제 한국경제     46536    0.551     0.539       0.795

## Daily rank IC (2020~2025 pooled)
outlet           timing  horizon year  avg_N  n_days  mean_ic   t_nw  hit_rate
  매일경제 A same-day close        1  all 18.653    1357    0.028  3.825     0.535
  매일경제 A same-day close        5  all 18.653    1357    0.017  2.140     0.518
  매일경제 B next-day close        1  all 18.653    1357   -0.001 -0.159     0.501
  매일경제 B next-day close        5  all 18.653    1357    0.003  0.378     0.517
  서울경제 A same-day close        1  all 23.318    1441    0.049  7.825     0.560
  서울경제 A same-day close        5  all 23.318    1441    0.022  3.003     0.539
  서울경제 B next-day close        1  all 23.318    1441   -0.006 -0.951     0.493
  서울경제 B next-day close        5  all 23.318    1441   -0.003 -0.431     0.505
  한국경제 A same-day close        1  all 26.119    1429    0.034  4.905     0.569
  한국경제 A same-day close        5  all 26.119    1429    0.013  1.661     0.529
  한국경제 B next-day close        1  all 26.119    1430   -0.013 -1.967     0.487
  한국경제 B next-day close        5  all 26.119    1430   -0.003 -0.446     0.485
pooled A same-day close        1  all 50.370    1473    0.032  6.938     0.578
pooled A same-day close        5  all 50.370    1473    0.015  2.887     0.537
pooled B next-day close        1  all 50.370    1473   -0.006 -1.367     0.488
pooled B next-day close        5  all 50.370    1473   -0.001 -0.172     0.500

## Daily rank IC by year, timing B, horizon 1
outlet  pooled   매일경제   서울경제   한국경제
year                               
2020    -0.026  0.001 -0.007 -0.042
2021    -0.011 -0.002 -0.013 -0.012
2022     0.001 -0.013  0.000  0.007
2023     0.002  0.004 -0.003 -0.006
2024    -0.011 -0.018 -0.018 -0.028
2025     0.008  0.022  0.003  0.001

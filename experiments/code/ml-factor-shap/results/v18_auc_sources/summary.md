# AUC sources

run: results/v16_fulluniv_sentnone_feature  months: 72

## Single-factor monthly AUC and rank correlation with each model's score
 factor  auc_alone  corr_logit  corr_lgbm  corr_catboost
VOL_20D      0.487      -0.328     -0.431         -0.395
 RET_1M      0.487      -0.338     -0.383         -0.379
 RET_3M      0.486      -0.394     -0.431         -0.424
RET_12M      0.500      -0.170     -0.220         -0.212
    PBR      0.473      -0.467     -0.310         -0.322
    ROE      0.532       0.392      0.230          0.251
  lmcap      0.525       0.063      0.064          0.076

## Monthly AUC of the score vs of its residual (same rows)
   model fset                          controls  rows_used  auc_score  auc_residual
   logit firm                               vol      1.000      0.550         0.546
   logit firm                              size      1.000      0.550         0.548
   logit firm                          reversal      1.000      0.550         0.547
   logit firm                vol+size+rev+mom12      0.998      0.550         0.539
   logit firm          value+quality (PBR, ROE)      0.999      0.550         0.529
   logit firm ALL: vol+size+rev+mom12 + PBR+ROE      0.998      0.550         0.517
    lgbm firm                               vol      1.000      0.552         0.545
    lgbm firm                              size      1.000      0.552         0.552
    lgbm firm                          reversal      1.000      0.552         0.550
    lgbm firm                vol+size+rev+mom12      0.998      0.552         0.539
    lgbm firm          value+quality (PBR, ROE)      0.999      0.552         0.540
    lgbm firm ALL: vol+size+rev+mom12 + PBR+ROE      0.998      0.553         0.531
catboost firm                               vol      1.000      0.553         0.546
catboost firm                              size      1.000      0.553         0.553
catboost firm                          reversal      1.000      0.554         0.551
catboost firm                vol+size+rev+mom12      0.998      0.553         0.540
catboost firm          value+quality (PBR, ROE)      0.999      0.554         0.541
catboost firm ALL: vol+size+rev+mom12 + PBR+ROE      0.998      0.554         0.529

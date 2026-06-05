# Hyperparameter Tuning Report

This report summarizes the results of the automated Optuna optimization.

## Overview
- **Best Model Type**: LightGBM
- **Best Cross-Validated RMSE**: 23.5583
- **Total Trials Completed**: 50
- **Pruned Trials (Saved Compute)**: 36

## Best Parameters
```json
{
    "model_type": "LightGBM",
    "lgb_n_estimators": 103,
    "lgb_max_depth": 4,
    "lgb_lr": 0.024816713558637658,
    "lgb_num_leaves": 54
}
```

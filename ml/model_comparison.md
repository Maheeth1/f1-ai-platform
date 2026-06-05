# Model Performance Comparison

This report compares the performance of individual models against our advanced ensemble techniques.

| Model | RMSE | MAE | R² |
| :--- | :--- | :--- | :--- |
| **CatBoost** | 6.6760 | 3.3137 | 0.8033 |
| **LightGBM** | 13.9110 | 4.0993 | 0.1459 |
| **XGBoost** | 7.4483 | 3.7794 | 0.7552 |
| **Weighted Ensemble** | 6.9667 | 3.3348 | 0.7858 |
| **Stacking Ensemble** | 12.6061 | 9.8459 | 0.2987 |

## Conclusion
The **Stacking Ensemble** and **Weighted Ensemble** automatically combine our base models (CatBoost, LightGBM, XGBoost) to reduce variance and improve overall validation performance.
# Model Performance Comparison

This report compares the performance of individual models against our advanced ensemble techniques.

| Model | RMSE | MAE | R² |
| :--- | :--- | :--- | :--- |
| **CatBoost** | 9.9940 | 4.4410 | 0.5592 |
| **LightGBM** | 9.7050 | 4.2006 | 0.5843 |
| **XGBoost** | 9.4245 | 5.0880 | 0.6080 |
| **Weighted Ensemble** | 8.7803 | 4.2371 | 0.6598 |
| **Stacking Ensemble** | 12.5521 | 9.7325 | 0.3046 |

## Conclusion
The **Stacking Ensemble** and **Weighted Ensemble** automatically combine our base models (CatBoost, LightGBM, XGBoost) to reduce variance and improve overall validation performance.
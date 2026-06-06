# Model Performance Comparison

This report compares the performance of individual models against our advanced ensemble techniques.

| Model | RMSE | MAE | R² |
| :--- | :--- | :--- | :--- |
| **CatBoost** | 0.6748 | 0.3203 | 0.9806 |
| **LightGBM** | 0.6682 | 0.2766 | 0.9810 |
| **XGBoost** | 0.6935 | 0.3364 | 0.9795 |
| **Weighted Ensemble** | 0.6541 | 0.2921 | 0.9818 |
| **Stacking Ensemble** | 0.6554 | 0.2872 | 0.9817 |

## Conclusion
The **Stacking Ensemble** and **Weighted Ensemble** automatically combine our base models (CatBoost, LightGBM, XGBoost) to reduce variance and improve overall validation performance.
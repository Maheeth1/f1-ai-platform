# Validation Strategy Comparison Report

This report compares three different cross-validation strategies using a baseline LightGBM model. Notice how Random Split often shows overly optimistic performance due to temporal leakage.

| Strategy | RMSE | MAE | R² |
| :--- | :--- | :--- | :--- |
| **Random Split** | 8.7636 | 3.1076 | 0.9051 |
| **GroupKFold** | 20.6177 | 6.7608 | 0.3848 |
| **TimeSplit** | 20.8956 | 4.8123 | 0.4056 |

## Conclusion
Based on motorsport realities, **TimeSplit** (TimeSeriesSplit) was automatically selected as the most realistic validation strategy for the final model training because it strictly prevents the model from seeing future data during training.

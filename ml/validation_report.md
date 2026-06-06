# Validation Strategy Comparison Report

This report compares three different cross-validation strategies using a baseline LightGBM model. Notice how Random Split often shows overly optimistic performance due to temporal leakage.

| Strategy | RMSE | MAE | R² |
| :--- | :--- | :--- | :--- |
| **Random Split** | 0.6140 | 0.2558 | 0.9834 |
| **GroupKFold** | 0.6631 | 0.2896 | 0.9806 |
| **TimeSplit** | 0.6727 | 0.2906 | 0.9799 |

## Conclusion
Based on motorsport realities, **TimeSplit** (TimeSeriesSplit) was automatically selected as the most realistic validation strategy for the final model training because it strictly prevents the model from seeing future data during training.

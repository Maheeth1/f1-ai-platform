import numpy as pd
import numpy as np
from typing import Dict, Any, Tuple

class ConfidenceEstimator:
    @staticmethod
    def estimate_confidence(
        model: Any, 
        processed_df: pd.DataFrame, 
        prediction: float, 
        metadata: Dict[str, Any]
    ) -> Tuple[float, float, float, Dict[str, Any]]:
        """
        Estimates confidence intervals and scores.
        Returns: (lower_bound, upper_bound, confidence_score, report_dict)
        """
        method_used = "unknown"
        lower_bound = prediction
        upper_bound = prediction
        
        # 1. Try Ensemble Variance
        if hasattr(model, "estimators_"):
            try:
                # E.g. RandomForestRegressor or StackingRegressor
                preds = []
                for estimator in model.estimators_:
                    # Need to check if estimator takes the df directly or needs transformation
                    # For simplicity, assuming pipeline handles it or estimator can predict
                    preds.append(estimator.predict(processed_df)[0])
                
                std_dev = np.std(preds)
                # 95% Confidence Interval
                lower_bound = prediction - (1.96 * std_dev)
                upper_bound = prediction + (1.96 * std_dev)
                method_used = "ensemble_variance"
            except Exception:
                pass
                
        # 2. Try Quantile Regression / Stored Quantiles (Mock logic for future proofing)
        elif hasattr(model, "predict_quantiles"):
            try:
                quantiles = model.predict_quantiles(processed_df, quantiles=[0.05, 0.95])
                lower_bound = quantiles[0][0]
                upper_bound = quantiles[0][1]
                method_used = "quantile_regression"
            except Exception:
                pass
                
        # 3. Fallback to Parametric RMSE
        if method_used == "unknown":
            # Assume metadata contains metrics dict with RMSE
            metrics = metadata.get("metrics", {}) if isinstance(metadata, dict) else {}
            rmse = metrics.get("RMSE", 0.5) # Default fallback
            
            lower_bound = prediction - (1.96 * rmse)
            upper_bound = prediction + (1.96 * rmse)
            method_used = "parametric_rmse"
            
        # 4. Calculate Confidence Score (0-100)
        # Using a simple heuristic based on the relative width of the interval
        interval_width = upper_bound - lower_bound
        if prediction == 0:
            confidence_score = 0.0
        else:
            # Example: If interval is 20% of prediction, score is 80.
            relative_width = (interval_width / abs(prediction))
            confidence_score = max(0.0, 100.0 - (relative_width * 100.0))
            confidence_score = min(100.0, confidence_score)
            
        report = {
            "method": method_used,
            "interval_width": round(interval_width, 4),
            "std_error_approx": round((upper_bound - lower_bound) / (2 * 1.96), 4)
        }
        
        return round(lower_bound, 4), round(upper_bound, 4), round(confidence_score, 2), report

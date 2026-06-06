import numpy as np
import pandas as pd
from typing import Dict, Any, List
from app.services.inference_service import InferenceService
from app.schemas.prediction import PredictionRequest

class MonteCarloSimulator:
    def __init__(self):
        self.inference_service = InferenceService()
        
    def run_simulation(self, base_request: PredictionRequest, iterations: int = 100) -> Dict[str, Any]:
        """
        Runs a Monte Carlo simulation by perturbing environment variables (TrackTemp, AirTemp)
        and predicting the resulting LapTime distribution.
        """
        base_features = base_request.model_dump()
        
        # We will create a dataframe with `iterations` rows of the base features
        df = pd.DataFrame([base_features] * iterations)
        
        # Perturb TrackTemp (normal distribution, mean=0, std=3.0)
        track_temp_noise = np.random.normal(0, 3.0, iterations)
        df['TrackTemp'] = df['TrackTemp'] + track_temp_noise
        
        # Perturb AirTemp (normal distribution, mean=0, std=2.0)
        air_temp_noise = np.random.normal(0, 2.0, iterations)
        df['AirTemp'] = df['AirTemp'] + air_temp_noise
        
        # Perturb TyreLife to simulate unknown degradation (std=2.0 laps)
        tyre_noise = np.random.normal(0, 2.0, iterations).round()
        df['TyreLife'] = np.maximum(1.0, df['TyreLife'] + tyre_noise) # cannot be less than 1 lap
        
        # Batch Predict
        from app.schemas.prediction import BatchPredictionRequest
        requests = [PredictionRequest(**row) for row in df.to_dict('records')]
        batch_request = BatchPredictionRequest(requests=requests)
        
        batch_response = self.inference_service.predict_batch("LapTimeSeconds", batch_request)
        
        predictions = [r.prediction for r in batch_response.responses]
        
        return {
            "mean_lap_time": round(np.mean(predictions), 4),
            "median_lap_time": round(np.median(predictions), 4),
            "p5_lap_time": round(np.percentile(predictions, 5), 4),
            "p95_lap_time": round(np.percentile(predictions, 95), 4),
            "std_dev": round(np.std(predictions), 4),
            "iterations": iterations,
            "raw_distribution": predictions
        }

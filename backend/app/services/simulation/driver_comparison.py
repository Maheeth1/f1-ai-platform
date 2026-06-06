import copy
from typing import Dict, Any
from app.services.inference_service import InferenceService
from app.schemas.prediction import PredictionRequest, BatchPredictionRequest

class DriverComparisonEngine:
    def __init__(self):
        self.inference_service = InferenceService()
        
    def compare_drivers(self, base_request: PredictionRequest, driver_1: str, driver_2: str) -> Dict[str, Any]:
        """
        Takes a base car/weather state and predicts a lap for two different drivers.
        Returns the head-to-head performance delta.
        """
        req1 = copy.deepcopy(base_request.model_dump())
        req1['Driver'] = driver_1
        
        req2 = copy.deepcopy(base_request.model_dump())
        req2['Driver'] = driver_2
        
        batch_request = BatchPredictionRequest(requests=[
            PredictionRequest(**req1),
            PredictionRequest(**req2)
        ])
        
        batch_response = self.inference_service.predict_batch("LapTimeSeconds", batch_request)
        
        p1 = batch_response.responses[0].prediction
        p2 = batch_response.responses[1].prediction
        
        delta = round(p1 - p2, 4)
        winner = driver_1 if delta < 0 else driver_2 if delta > 0 else "Tie"
        
        return {
            "driver_1": driver_1,
            "driver_1_predicted_lap": p1,
            "driver_2": driver_2,
            "driver_2_predicted_lap": p2,
            "time_delta_sec": abs(delta),
            "faster_driver": winner,
            "base_conditions": base_request.model_dump()
        }

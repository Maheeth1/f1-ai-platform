import copy
from typing import Dict, Any, List
from app.services.inference_service import InferenceService
from app.schemas.prediction import PredictionRequest, BatchPredictionRequest

class StrategySimulator:
    def __init__(self):
        self.inference_service = InferenceService()
        self.pitstop_penalty_sec = 25.0
        
    def simulate_stint(self, base_request: PredictionRequest, laps: int, pit_at_lap: int = -1) -> Dict[str, Any]:
        """
        Simulates a sequence of laps. The tyre life degrades by 1 each lap.
        Fuel/LapNumber increases each lap.
        If pit_at_lap is reached, it adds a pit stop penalty and resets TyreLife.
        """
        requests = []
        current_req = copy.deepcopy(base_request.model_dump())
        
        for lap_offset in range(laps):
            if lap_offset > 0:
                current_req['LapNumber'] += 1
                current_req['TyreLife'] += 1
                
            if lap_offset == pit_at_lap:
                current_req['TyreLife'] = 1.0 # Fresh tyres
                
            requests.append(PredictionRequest(**current_req))
            
        batch_request = BatchPredictionRequest(requests=requests)
        batch_response = self.inference_service.predict_batch("LapTimeSeconds", batch_request)
        
        predictions = [r.prediction for r in batch_response.responses]
        
        # Apply pitstop penalty to the total race time
        total_time = sum(predictions)
        if pit_at_lap >= 0:
            total_time += self.pitstop_penalty_sec
            
        return {
            "total_race_time_sec": round(total_time, 2),
            "lap_times": predictions,
            "avg_lap_time": round(total_time / laps, 3),
            "pit_laps": [pit_at_lap] if pit_at_lap >= 0 else []
        }
        
    def find_optimal_pitstop(self, base_request: PredictionRequest, total_laps: int) -> Dict[str, Any]:
        """
        Evaluates a 1-stop strategy across all possible pit laps to find the minimum total race time.
        """
        best_time = float('inf')
        best_lap = -1
        results = {}
        
        for pit_lap in range(1, total_laps):
            result = self.simulate_stint(base_request, total_laps, pit_at_lap=pit_lap)
            time = result["total_race_time_sec"]
            if time < best_time:
                best_time = time
                best_lap = pit_lap
                results = result
                
        return {
            "optimal_pit_lap": best_lap,
            "total_race_time_sec": best_time,
            "lap_times": results["lap_times"]
        }

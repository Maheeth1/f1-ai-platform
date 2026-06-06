import pandas as pd
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.model_registry import ModelRegistry
from app.core.logger import logger

class InferenceService:
    def predict(self, target: str, data: PredictionRequest) -> PredictionResponse:
        model = ModelRegistry.get_active_model(target)
        if model is None:
            raise ValueError(f"Active model for target '{target}' is not loaded.")
        
        input_df = pd.DataFrame({
            "Driver": [data.Driver],
            "LapNumber": [data.LapNumber],
            "TyreLife": [data.TyreLife]
        })
        
        logger.info(f"Running {target} inference for driver {data.Driver}")
        prediction = model.predict(input_df)
        
        return PredictionResponse(
            predicted_position=round(float(prediction[0]), 2)
        )

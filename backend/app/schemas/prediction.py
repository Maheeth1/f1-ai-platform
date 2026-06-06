from pydantic import BaseModel, ConfigDict, Field
from typing import List

class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra='allow')
    Driver: str
    LapNumber: int = Field(default=1)
    TyreLife: int = Field(default=0)

class BatchPredictionRequest(BaseModel):
    requests: List[PredictionRequest]

class PredictionResponse(BaseModel):
    prediction: float
    confidence: float
    model_version: str
    latency_ms: float

class BatchPredictionResponse(BaseModel):
    responses: List[PredictionResponse]

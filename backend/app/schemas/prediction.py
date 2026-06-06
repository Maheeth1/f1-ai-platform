from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    Driver: int = Field(..., ge=0)
    LapNumber: int = Field(..., ge=1)
    TyreLife: int = Field(..., ge=0)

class PredictionResponse(BaseModel):
    predicted_position: float

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.inference_service import InferenceService
from app.api.dependencies import get_inference_service

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
def predict(
    data: PredictionRequest,
    inference_service: InferenceService = Depends(get_inference_service)
):
    try:
        return inference_service.predict(data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/sample-request")
def sample_request():
    return {
        "Driver": 5,
        "LapNumber": 20,
        "TyreLife": 15
    }

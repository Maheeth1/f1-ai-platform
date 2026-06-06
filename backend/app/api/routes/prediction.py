from fastapi import APIRouter, Depends, HTTPException, Path
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.inference_service import InferenceService
from app.api.dependencies import get_inference_service, require_model_loaded_for_target

router = APIRouter()

@router.post("/{target}/predict", response_model=PredictionResponse)
def predict(
    data: PredictionRequest,
    target: str = Depends(require_model_loaded_for_target),
    inference_service: InferenceService = Depends(get_inference_service)
):
    try:
        return inference_service.predict(target, data)
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

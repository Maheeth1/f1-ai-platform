from fastapi import APIRouter, Depends, HTTPException, Request
from app.schemas.prediction import PredictionRequest, PredictionResponse, BatchPredictionRequest, BatchPredictionResponse
from app.services.inference_service import InferenceService
from app.api.dependencies import get_inference_service, require_model_loaded_for_target, get_current_user
from app.api.middleware.cache import cached
from app.api.middleware.rate_limit import rate_limit

router = APIRouter()

@router.post("/{target}/predict", response_model=PredictionResponse)
@rate_limit(requests=100, window=60)
@cached(ttl=3600)
def predict(
    request: Request,
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

@router.post("/{target}/predict/batch", response_model=BatchPredictionResponse)
@rate_limit(requests=50, window=60)
@cached(ttl=3600)
def predict_batch(
    request: Request,
    data: BatchPredictionRequest,
    target: str = Depends(require_model_loaded_for_target),
    inference_service: InferenceService = Depends(get_inference_service)
):
    try:
        return inference_service.predict_batch(target, data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/sample-request")
def sample_request():
    return {
        "Driver": "VER",
        "LapNumber": 20,
        "TyreLife": 15
    }

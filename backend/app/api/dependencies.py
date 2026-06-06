from fastapi import HTTPException, Path
from app.services.inference_service import InferenceService
from app.services.model_registry import ModelRegistry

def require_model_loaded_for_target(target: str = Path(...)):
    if ModelRegistry.get_active_model(target) is None:
        raise HTTPException(
            status_code=503,
            detail=f"Active model for target '{target}' not loaded"
        )
    return target

def get_inference_service() -> InferenceService:
    return InferenceService()

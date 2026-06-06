from fastapi import HTTPException
from app.services.inference_service import InferenceService
from app.services.model_registry import ModelRegistry

def require_model_loaded():
    if not ModelRegistry.is_loaded():
        raise HTTPException(
            status_code=500,
            detail="Model not loaded"
        )

def get_inference_service() -> InferenceService:
    require_model_loaded()
    return InferenceService()

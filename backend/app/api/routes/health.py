from fastapi import APIRouter
from app.services.model_registry import ModelRegistry

router = APIRouter()

@router.get("/")
def root():
    return {
        "message": "F1 AI Platform Running"
    }

@router.get("/health")
def health():
    state = ModelRegistry.get_registry_state()
    active_models = {
        target: info["active_version"] is not None
        for target, info in state.items()
    }
    return {
        "status": "healthy",
        "active_models": active_models
    }

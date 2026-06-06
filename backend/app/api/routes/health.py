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
    return {
        "status": "healthy",
        "model_loaded": ModelRegistry.is_loaded()
    }

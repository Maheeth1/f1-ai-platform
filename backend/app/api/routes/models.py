from fastapi import APIRouter, Depends
from app.api.dependencies import require_model_loaded
from app.services.model_registry import ModelRegistry

router = APIRouter()

@router.get("/model-info", dependencies=[Depends(require_model_loaded)])
def model_info():
    model = ModelRegistry.get_model()
    return {
        "model_type": type(model).__name__,
        "features": [
            "Driver",
            "LapNumber",
            "TyreLife"
        ]
    }

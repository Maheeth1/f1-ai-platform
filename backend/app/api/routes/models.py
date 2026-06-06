from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.services.model_registry import ModelRegistry
from app.schemas.registry import (
    ModelRegistryResponse,
    ActiveModelsResponse,
    ModelRegistrationRequest,
    ModelSwitchRequest
)

router = APIRouter()

@router.get("", response_model=ModelRegistryResponse)
def get_registry():
    """Returns the full model registry state."""
    return ModelRegistry.get_registry_state()

@router.get("/active", response_model=ActiveModelsResponse)
def get_active_models():
    """Returns the active model metadata for all targets."""
    state = ModelRegistry.get_registry_state()
    active_models = {}
    for target, info in state.items():
        active_version = info.get("active_version")
        if active_version:
            version_info = next((v for v in info["versions"] if v["version"] == active_version), None)
            active_models[target] = version_info
        else:
            active_models[target] = None
    return ActiveModelsResponse(active_models=active_models)

@router.post("/switch")
def switch_active_model(req: ModelSwitchRequest):
    """Switches the active model for a specific target."""
    try:
        ModelRegistry.switch_active_model(req.target, req.version)
        return {"message": f"Successfully switched {req.target} to version {req.version}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/rollback/{target}")
def rollback_model(target: str):
    """Rolls back the active model to the previous version."""
    try:
        prev_version = ModelRegistry.rollback_model(target)
        return {"message": f"Successfully rolled back {target} to version {prev_version}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/register")
def register_model(req: ModelRegistrationRequest):
    """Registers a new model version (internal use / CI-CD)."""
    try:
        ModelRegistry.register_model(
            target=req.target,
            version=req.version,
            path=req.path,
            metrics=req.metrics,
            metadata=req.metadata
        )
        return {"message": f"Successfully registered {req.target} version {req.version}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/info/{target}")
def model_info(target: str):
    """Returns features and model_type for the active target model."""
    model = ModelRegistry.get_active_model(target)
    if not model:
        raise HTTPException(status_code=503, detail=f"Active model for {target} not loaded")
    return {
        "model_type": type(model).__name__,
        "target": target
    }

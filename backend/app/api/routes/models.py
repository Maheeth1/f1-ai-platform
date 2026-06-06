from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from typing import Dict, Any, List
from app.services.model_registry import ModelRegistry
from app.services.huggingface_service import HuggingFaceService
from app.api.dependencies import get_current_user
from app.api.middleware.cache import cached
from app.schemas.registry import (
    ModelRegistryResponse,
    ActiveModelsResponse,
    ModelRegistrationRequest,
    ModelSwitchRequest,
    HFSyncRequest,
    HFModelsResponse
)

router = APIRouter()

@router.get("", response_model=ModelRegistryResponse)
@cached(ttl=60)
def get_registry(request: Request):
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

@router.get("/hf/{target}", response_model=HFModelsResponse)
@cached(ttl=300)
def list_hf_models(target: str, request: Request):
    """Lists all available versions for a given target on Hugging Face."""
    try:
        versions = HuggingFaceService.list_versions(target)
        return HFModelsResponse(target=target, available_versions=versions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
def sync_hf_model(req: HFSyncRequest, current_user: str = Depends(get_current_user)):
    """Downloads a model from HF, registers it locally, and activates it."""
    try:
        versions = HuggingFaceService.list_versions(req.target)
        if not versions:
            raise HTTPException(status_code=404, detail=f"No HF versions found for {req.target}")
            
        version_to_sync = req.version or versions[0]
        
        # Avoid re-downloading if already registered
        state = ModelRegistry.get_registry_state()
        target_info = state.get(req.target, {"versions": []})
        already_registered = any(v["version"] == version_to_sync for v in target_info["versions"])
        
        if not already_registered:
            hf_data = HuggingFaceService.download_version(req.target, version_to_sync)
            ModelRegistry.register_model(
                target=req.target,
                version=version_to_sync,
                path=hf_data["path"],
                metrics=hf_data["metrics"],
                metadata=hf_data["metadata"]
            )
            
        # Switch to it
        ModelRegistry.switch_active_model(req.target, version_to_sync)
        return {"message": f"Successfully synced and activated {req.target} version {version_to_sync}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/switch")
def switch_active_model(req: ModelSwitchRequest):
    """Switches the active model for a specific target locally."""
    try:
        ModelRegistry.switch_active_model(req.target, req.version)
        return {"message": f"Successfully switched {req.target} to version {req.version}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/rollback/{target}")
def rollback_model(target: str):
    """Rolls back the active model to the previous version locally."""
    try:
        prev_version = ModelRegistry.rollback_model(target)
        return {"message": f"Successfully rolled back {target} to version {prev_version}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/register")
def register_model(req: ModelRegistrationRequest):
    """Registers a new model version (internal use)."""
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

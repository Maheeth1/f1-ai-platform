from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class ModelVersionInfo(BaseModel):
    version: str
    path: str
    registered_at: str
    metrics: Dict[str, Any]
    metadata: Dict[str, Any]

class TargetRegistryInfo(BaseModel):
    active_version: Optional[str]
    versions: List[ModelVersionInfo]

class ModelRegistryResponse(BaseModel):
    laptime: TargetRegistryInfo
    gridposition: TargetRegistryInfo
    simulation: TargetRegistryInfo

class ModelRegistrationRequest(BaseModel):
    target: str
    version: str
    path: str
    metrics: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

class ModelSwitchRequest(BaseModel):
    target: str
    version: str

class ActiveModelsResponse(BaseModel):
    active_models: Dict[str, Optional[ModelVersionInfo]]

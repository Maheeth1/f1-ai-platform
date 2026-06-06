import json
import os
import joblib
from datetime import datetime
from typing import Dict, Any, Optional
from app.core.logger import logger
from app.core.config import MODEL_DIR

REGISTRY_PATH = MODEL_DIR / "registry.json"

class ModelRegistry:
    # Keeps track of models loaded in memory for fast inference
    # Format: {"laptime": model_object, "gridposition": model_object, ...}
    _active_models: Dict[str, Any] = {}
    
    @classmethod
    def _get_registry_data(cls) -> Dict[str, Any]:
        if not REGISTRY_PATH.exists():
            return {
                "LapTimeSeconds": {"active_version": None, "versions": []},
                "Position": {"active_version": None, "versions": []}
            }
        with open(REGISTRY_PATH, 'r') as f:
            return json.load(f)

    @classmethod
    def _save_registry_data(cls, data: Dict[str, Any]):
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(REGISTRY_PATH, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def register_model(cls, target: str, version: str, metrics: Dict[str, Any] = None, metadata: Dict[str, Any] = None):
        """Registers a new model version for a given target."""
        registry = cls._get_registry_data()
        
        if target not in registry:
            registry[target] = {"active_version": None, "versions": []}
            
        # Check if version already exists
        for i, v in enumerate(registry[target]["versions"]):
            if v["version"] == version:
                logger.info(f"Model {version} for {target} was already registered.")
                return
        new_version = {
            "version": version,
            "registered_at": datetime.utcnow().isoformat(),
            "metrics": metrics or {},
            "metadata": metadata or {}
        }
        
        registry[target]["versions"].append(new_version)
        cls._save_registry_data(registry)
        logger.info(f"Successfully registered model {version} for {target}")

    @classmethod
    def load_model(cls, target: str, version: Optional[str] = None):
        """Loads a model into memory. If version is None, loads the active version."""
        registry = cls._get_registry_data()
        
        if target not in registry:
            raise ValueError(f"Target {target} not found in registry")
            
        target_info = registry[target]
        version_to_load = version or target_info["active_version"]
        
        if not version_to_load:
            logger.warning(f"No active version found for {target} to load")
            return None
            
        # Find the version info
        version_info = next((v for v in target_info["versions"] if v["version"] == version_to_load), None)
        if not version_info:
            raise ValueError(f"Version {version_to_load} not found for target {target}")
            
        # Dynamically reconstruct the local path
        # This prevents absolute Windows paths from crashing Linux servers
        target_dir = MODEL_DIR / target / version_to_load
        path = target_dir / "model.pkl"
        
        if not path.exists():
            logger.error(f"Model file not found at {path}")
            raise FileNotFoundError(f"Model file not found at {path}")
            
        try:
            logger.info(f"Loading model from: {path}")
            model = joblib.load(path)
            
            encoder = None
            encoder_path = target_dir / "encoder.pkl"
            if encoder_path.exists():
                encoder = joblib.load(encoder_path)
                
            scaler = None
            scaler_path = target_dir / "scaler.pkl"
            if scaler_path.exists():
                scaler = joblib.load(scaler_path)
                
            features = []
            features_path = target_dir / "feature_list.json"
            if features_path.exists():
                with open(features_path, "r", encoding='utf-8') as f:
                    import json
                    features = json.load(f).get("features", [])
            
            cls._active_models[target] = {
                "model": model,
                "encoder": encoder,
                "scaler": scaler,
                "features": features,
                "version": version_to_load
            }
            logger.info(f"SUCCESS: Model {version_to_load} for {target} loaded into memory with artifacts.")
        except Exception as e:
            logger.error(f"ERROR: Failed to load model from {path}: {e}")
            raise e

    @classmethod
    def rollback_model(cls, target: str):
        """Rolls back the active model to the previous version, if available."""
        registry = cls._get_registry_data()
        if target not in registry:
            raise ValueError(f"Target {target} not found in registry")
            
        target_info = registry[target]
        versions = target_info["versions"]
        
        if len(versions) < 2:
            raise ValueError(f"Not enough versions to rollback for target {target}")
            
        # Assuming versions are appended in chronological order
        current_active = target_info["active_version"]
        
        # Find index of current active
        idx = -1
        for i, v in enumerate(versions):
            if v["version"] == current_active:
                idx = i
                break
                
        if idx <= 0:
            raise ValueError(f"Cannot rollback: Current active version is the oldest or not found.")
            
        previous_version = versions[idx - 1]["version"]
        cls.switch_active_model(target, previous_version)
        logger.info(f"Rolled back {target} to version {previous_version}")
        return previous_version

    @classmethod
    def switch_active_model(cls, target: str, version: str):
        """Switches the active model for a target and loads it into memory."""
        registry = cls._get_registry_data()
        if target not in registry:
            raise ValueError(f"Target {target} not found in registry")
            
        # Validate version exists
        version_exists = any(v["version"] == version for v in registry[target]["versions"])
        if not version_exists:
            raise ValueError(f"Version {version} not found for target {target}")
            
        registry[target]["active_version"] = version
        cls._save_registry_data(registry)
        
        # Attempt to load it into memory
        cls.load_model(target, version)

    @classmethod
    def get_active_model(cls, target: str):
        """Returns the in-memory active model for a target."""
        return cls._active_models.get(target)

    @classmethod
    def get_active_version_info(cls, target: str) -> Optional[Dict[str, Any]]:
        """Returns metadata for the active version of a target."""
        registry = cls._get_registry_data()
        if target not in registry:
            return None
        active_version = registry[target]["active_version"]
        if not active_version:
            return None
        return next((v for v in registry[target]["versions"] if v["version"] == active_version), None)

    @classmethod
    def get_registry_state(cls) -> Dict[str, Any]:
        """Returns the full registry state."""
        return cls._get_registry_data()

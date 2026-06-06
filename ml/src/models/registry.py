import os
import json
import joblib
from datetime import datetime
from pathlib import Path
from huggingface_hub import HfApi
from src.utils.logger import get_logger

logger = get_logger(__name__)

ARTIFACTS_DIR = Path(__file__).resolve().parent.parent.parent / "artifacts"

def save_model(model, target_name, metrics, feature_list, encoder=None, scaler=None, model_type="StackingEnsemble"):
    """
    Saves a trained model and its associated metadata/preprocessing artifacts
    to a versioned directory in ml/artifacts/.
    """
    version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    target_dir = ARTIFACTS_DIR / target_name / version
    
    target_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Creating model artifact directory at: {target_dir}")
    
    # 1. Save Model
    model_path = target_dir / "model.pkl"
    joblib.dump(model, model_path)
    
    # 2. Save Preprocessors (if provided)
    if encoder is not None:
        joblib.dump(encoder, target_dir / "encoder.pkl")
    if scaler is not None:
        joblib.dump(scaler, target_dir / "scaler.pkl")
        
    # 3. Save Feature List
    feature_path = target_dir / "feature_list.json"
    with open(feature_path, "w", encoding='utf-8') as f:
        json.dump({"features": list(feature_list)}, f, indent=4)
        
    # 4. Save Metadata
    metadata = {
        "training_date": datetime.now().isoformat(),
        "model_type": model_type,
        "target": target_name,
        "version": version,
        "metrics": metrics,
        "dataset_version": "latest" # Could be dynamic in the future
    }
    
    meta_path = target_dir / "metadata.json"
    with open(meta_path, "w", encoding='utf-8') as f:
        json.dump(metadata, f, indent=4)
        
    logger.info(f"Successfully saved all artifacts locally for {target_name} ({version}).")
    
    # 5. Push to Hugging Face
    hf_token = os.environ.get("HF_TOKEN")
    hf_repo_id = os.environ.get("HF_REPO_ID", "Maheeth1/f1-race-predictor")
    
    if hf_token:
        try:
            logger.info(f"Pushing model {version} to Hugging Face repository: {hf_repo_id}")
            api = HfApi()
            
            # Create a path in the repo like: target_name/version/
            repo_path_prefix = f"{target_name}/{version}"
            
            api.upload_folder(
                folder_path=str(target_dir),
                path_in_repo=repo_path_prefix,
                repo_id=hf_repo_id,
                repo_type="model",
                token=hf_token,
                commit_message=f"Auto-upload: {target_name} model {version}"
            )
            logger.info("Successfully pushed model artifacts to Hugging Face.")
        except Exception as e:
            logger.error(f"Failed to push to Hugging Face: {e}")
    else:
        logger.warning("HF_TOKEN not set. Skipping automatic push to Hugging Face.")
        
    return version

def load_model(target_name, version="latest"):
    """
    Loads the model, metadata, and feature list for a given target.
    If version is 'latest', automatically finds the most recently saved version.
    """
    target_dir = ARTIFACTS_DIR / target_name
    
    if not target_dir.exists():
        raise FileNotFoundError(f"No artifacts found for target: {target_name}")
        
    if version == "latest":
        # Find the latest version by sorting directory names
        versions = [d.name for d in target_dir.iterdir() if d.is_dir() and d.name.startswith("v")]
        if not versions:
            raise FileNotFoundError(f"No version directories found in {target_dir}")
        versions.sort(reverse=True)
        version = versions[0]
        logger.info(f"Resolved 'latest' version to {version}")
        
    version_dir = target_dir / version
    if not version_dir.exists():
        raise FileNotFoundError(f"Version {version} not found in {target_dir}")
        
    logger.info(f"Loading artifacts from {version_dir}...")
    
    # Load Model
    model = joblib.load(version_dir / "model.pkl")
    
    # Load Preprocessors (optional)
    encoder = None
    if (version_dir / "encoder.pkl").exists():
        encoder = joblib.load(version_dir / "encoder.pkl")
        
    scaler = None
    if (version_dir / "scaler.pkl").exists():
        scaler = joblib.load(version_dir / "scaler.pkl")
        
    # Load Features
    with open(version_dir / "feature_list.json", "r", encoding='utf-8') as f:
        feature_list = json.load(f)["features"]
        
    # Load Metadata
    with open(version_dir / "metadata.json", "r", encoding='utf-8') as f:
        metadata = json.load(f)
        
    return {
        "model": model,
        "encoder": encoder,
        "scaler": scaler,
        "features": feature_list,
        "metadata": metadata
    }

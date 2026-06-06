import os
import json
from typing import List, Optional, Dict, Any
from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.utils import EntryNotFoundError
from app.core.config import settings, MODEL_DIR
from app.core.logger import logger

class HuggingFaceService:
    @staticmethod
    def list_versions(target: str) -> List[str]:
        """Queries the HF Hub to find all available version directories for a given target."""
        logger.info(f"Listing versions for {target} from {settings.model_repo_id}")
        api = HfApi()
        
        try:
            # We list the repo files and extract unique directories under the target
            # E.g., target/v20231010_120000/model.pkl
            files = api.list_repo_tree(
                repo_id=settings.model_repo_id,
                repo_type="model",
                token=settings.hf_token,
                path_in_repo=target
            )
            
            versions = set()
            for file_info in files:
                if isinstance(file_info, dict):
                    # For older hf_hub version dictionary formats
                    path = file_info.get("path", "")
                else:
                    path = getattr(file_info, "path", "")
                    
                # Path is like: laptime/v1.0.0/model.pkl
                parts = path.split('/')
                if len(parts) >= 2 and parts[0] == target:
                    versions.add(parts[1])
                    
            return sorted(list(versions), reverse=True)
            
        except EntryNotFoundError:
            logger.warning(f"No models found for target {target} in HF repo.")
            return []
        except Exception as e:
            logger.error(f"Error listing HF versions: {e}")
            raise e

    @staticmethod
    def download_version(target: str, version: str) -> Dict[str, Any]:
        """Downloads the model, metadata, and features from HF to the local backend/models/ directory."""
        logger.info(f"Downloading {target} version {version} from {settings.model_repo_id}")
        
        # Local target directory
        target_dir = MODEL_DIR / target / version
        target_dir.mkdir(parents=True, exist_ok=True)
        
        files_to_download = ["model.pkl", "metadata.json", "feature_list.json", "encoder.pkl", "scaler.pkl"]
        
        downloaded_paths = {}
        for filename in files_to_download:
            try:
                # E.g., laptime/v1.0.0/model.pkl
                repo_path = f"{target}/{version}/{filename}"
                local_path = hf_hub_download(
                    repo_id=settings.model_repo_id,
                    filename=repo_path,
                    token=settings.hf_token,
                    local_dir=str(MODEL_DIR)
                    # Note: hf_hub_download downloads to a cache dir by default, or specific local_dir
                    # It will preserve the target/version/filename structure in local_dir
                )
                downloaded_paths[filename] = local_path
            except EntryNotFoundError:
                if filename == "model.pkl":
                    logger.error(f"Missing core model.pkl for {target}/{version}")
                    raise
                else:
                    logger.warning(f"Missing {filename} for {target}/{version}, skipping.")
            except Exception as e:
                logger.error(f"Failed to download {filename}: {e}")
                raise e
                
        logger.info(f"Successfully downloaded {target} version {version} from HuggingFace.")
        
        # Return metadata and metrics (paths are constructed dynamically at runtime)
        metadata_path = downloaded_paths.get("metadata.json")
        
        metadata = {}
        metrics = {}
        if metadata_path and os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding='utf-8') as f:
                meta = json.load(f)
                metadata = meta
                metrics = meta.get("metrics", {})
                
        return {
            "metadata": metadata,
            "metrics": metrics
        }

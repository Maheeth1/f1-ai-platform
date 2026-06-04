import os
from huggingface_hub import HfApi, login
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.utils.logger import get_logger
from src.utils.config import ROOT_DIR

logger = get_logger(__name__)

def export_to_hf():
    """
    Uploads trained models and SHAP reports to Hugging Face Hub.
    """
    logger.info("Initializing Hugging Face Export...")
    
    # Authenticate
    token = os.environ.get("HF_TOKEN")
    if not token:
        logger.error("HF_TOKEN environment variable not found. Please set it or run `huggingface-cli login`")
        return
        
    login(token=token)
    api = HfApi()
    
    # Define repository name (username/repo-name)
    # Typically passed via environment variable or argument
    repo_id = os.environ.get("HF_REPO_ID", "YOUR_HF_USERNAME/f1-ai-models")
    
    if "YOUR_HF_USERNAME" in repo_id:
        logger.warning(f"Using default repo_id: {repo_id}. Please set HF_REPO_ID environment variable.")
        
    try:
        # Create repo if it doesn't exist
        api.create_repo(repo_id=repo_id, exist_ok=True, repo_type="model")
        logger.info(f"Repository {repo_id} ready.")
    except Exception as e:
        logger.error(f"Failed to create/access repo: {e}")
        return

    # Upload Models
    model_dir = ROOT_DIR / "ml" / "saved_models"
    if model_dir.exists():
        for model_file in model_dir.glob("*.joblib"):
            logger.info(f"Uploading {model_file.name}...")
            api.upload_file(
                path_or_fileobj=str(model_file),
                path_in_repo=f"models/{model_file.name}",
                repo_id=repo_id,
                repo_type="model"
            )
            
    # Upload SHAP Reports
    reports_dir = ROOT_DIR / "ml" / "reports"
    if reports_dir.exists():
        for report_file in reports_dir.glob("*.png"):
            logger.info(f"Uploading {report_file.name}...")
            api.upload_file(
                path_or_fileobj=str(report_file),
                path_in_repo=f"reports/{report_file.name}",
                repo_id=repo_id,
                repo_type="model"
            )
            
    logger.info(f"Successfully exported models and reports to Hugging Face: https://huggingface.co/{repo_id}")

if __name__ == "__main__":
    export_to_hf()

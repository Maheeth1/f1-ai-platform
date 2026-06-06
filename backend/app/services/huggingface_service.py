import os
from huggingface_hub import hf_hub_download
from app.core.config import settings
from app.core.logger import logger

class HuggingFaceService:
    @staticmethod
    def download_model() -> str:
        logger.info(f"Downloading model {settings.model_filename} from {settings.model_repo_id}")
        try:
            model_path = hf_hub_download(
                repo_id=settings.model_repo_id,
                filename=settings.model_filename,
                token=settings.hf_token
            )
            logger.info("Successfully downloaded model from HuggingFace.")
            return model_path
        except Exception as e:
            logger.error(f"Error downloading model: {e}")
            raise e

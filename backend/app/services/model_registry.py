import joblib
from app.core.logger import logger

class ModelRegistry:
    _model = None

    @classmethod
    def load_model(cls, model_path: str):
        try:
            cls._model = joblib.load(model_path)
            logger.info("SUCCESS: Model loaded into registry.")
        except Exception as e:
            logger.error(f"ERROR: Failed to load model: {e}")
            raise e

    @classmethod
    def get_model(cls):
        return cls._model

    @classmethod
    def is_loaded(cls) -> bool:
        return cls._model is not None

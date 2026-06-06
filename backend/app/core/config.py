import os
from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "F1 AI Platform API"
    description: str = "Formula 1 Race Prediction API"
    version: str = "1.0.0"
    
    hf_token: str | None = os.environ.get("HF_TOKEN")
    model_repo_id: str = "Maheeth1/f1-race-predictor"
    model_filename: str = "f1_model.pkl"

    # CORS
    cors_origins: list[str] = ["*"]
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]
    # Redis
    redis_url: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

settings = Settings()

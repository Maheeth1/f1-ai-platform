import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = BASE_DIR / "models"

class Settings(BaseModel):
    app_name: str = "F1 AI Platform API"
    description: str = "Formula 1 Race Prediction API"
    version: str = "1.0.0"
    
    hf_token: str | None = os.environ.get("HF_TOKEN")
    model_repo_id: str = "Maheeth1/f1-race-predictor"
    model_filename: str = "f1_model.pkl"

    # CORS
    cors_origins: list[str] = [
        "https://f1-ai.example.com", 
        "http://localhost:3000",
        "https://f1-ai-platform-phi.vercel.app"
    ]
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    def __init__(self, **data):
        super().__init__(**data)
        if env_cors := os.environ.get("CORS_ORIGINS"):
            self.cors_origins.extend([origin.strip() for origin in env_cors.split(",")])
    
    # Redis
    redis_url: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Security
    secret_key: str = os.environ.get("SECRET_KEY", "super-secret-dev-key")
    jwt_algorithm: str = os.environ.get("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    api_key: str = os.environ.get("API_KEY", "dev-api-key")

settings = Settings()

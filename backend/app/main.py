from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logger import logger
from app.services.huggingface_service import HuggingFaceService
from app.services.model_registry import ModelRegistry
from app.api.routes import health, models, prediction, metadata

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up F1 AI Platform API...")
    try:
        model_path = HuggingFaceService.download_model()
        ModelRegistry.load_model(model_path)
    except Exception as e:
        logger.error(f"Failed to load model during startup: {e}")
        # Not raising here to allow app to start even if HF fails (matches old behavior)
    
    yield
    
    # Shutdown
    logger.info("Shutting down F1 AI Platform API...")

app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.version,
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(models.router, tags=["Models"])
app.include_router(metadata.router, tags=["Metadata"])
app.include_router(prediction.router, tags=["Prediction"])

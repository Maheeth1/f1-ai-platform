import os
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
        # Check if laptime has any versions, if not, bootstrap from HF
        registry_state = ModelRegistry.get_registry_state()
        laptime_info = registry_state.get("laptime", {})
        if not laptime_info.get("versions"):
            logger.info("Bootstrapping initial laptime model from Hugging Face...")
            model_path = HuggingFaceService.download_model()
            ModelRegistry.register_model(
                target="laptime",
                version="v1.0.0",
                path=os.path.abspath(model_path),
                metadata={"source": "huggingface", "repo_id": settings.model_repo_id}
            )
            ModelRegistry.switch_active_model("laptime", "v1.0.0")
        
        # Load all active models into memory
        registry_state = ModelRegistry.get_registry_state()
        for target, info in registry_state.items():
            if info.get("active_version"):
                try:
                    ModelRegistry.load_model(target)
                except Exception as e:
                    logger.error(f"Failed to load active model for {target}: {e}")

    except Exception as e:
        logger.error(f"Error during startup: {e}")
    
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
app.include_router(models.router, prefix="/models", tags=["Models Registry"])
app.include_router(metadata.router, tags=["Metadata"])
app.include_router(prediction.router, tags=["Prediction"])

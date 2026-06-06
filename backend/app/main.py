import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logger import logger
from app.services.huggingface_service import HuggingFaceService
from app.services.model_registry import ModelRegistry
from app.api.routes import health, models, prediction, metadata, metrics, auth
from app.api.middleware.security import SecurityHeadersMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up F1 AI Platform API...")
    try:
        # Sync latest models from Hugging Face on startup for known targets
        targets_to_sync = ["laptime"]  # Add other targets as needed
        
        for target in targets_to_sync:
            try:
                versions = HuggingFaceService.list_versions(target)
                if versions:
                    latest_version = versions[0]
                    state = ModelRegistry.get_registry_state()
                    target_info = state.get(target, {"versions": []})
                    
                    # If we don't have this version, download and register it
                    already_registered = any(v["version"] == latest_version for v in target_info.get("versions", []))
                    if not already_registered:
                        logger.info(f"Syncing latest {target} model {latest_version} from Hugging Face...")
                        hf_data = HuggingFaceService.download_version(target, latest_version)
                        ModelRegistry.register_model(
                            target=target,
                            version=latest_version,
                            path=hf_data["path"],
                            metrics=hf_data["metrics"],
                            metadata=hf_data["metadata"]
                        )
                    
                    # Always activate the latest version on startup
                    ModelRegistry.switch_active_model(target, latest_version)
            except Exception as e:
                logger.error(f"Failed to sync {target} from HF during startup: {e}")

        
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

# Add Middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Prometheus Monitoring
Instrumentator().instrument(app).expose(app)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(models.router, prefix="/models", tags=["Models Registry"])
app.include_router(metadata.router, prefix="/metadata", tags=["Metadata"])
app.include_router(metrics.router, tags=["System"])
app.include_router(prediction.router, tags=["Prediction"])

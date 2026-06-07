import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings, MODEL_DIR
from app.core.logger import logger
from app.services.huggingface_service import HuggingFaceService
from app.services.model_registry import ModelRegistry
from app.api.routes import health, models, prediction, metadata, metrics, auth, simulation, ingest, analyst, data
from app.api.middleware.security import SecurityHeadersMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.db.database import engine
from app.db.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up F1 AI Platform API...")
    logger.info("Initializing database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info(f"Model directory resolved to: {MODEL_DIR}")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    try:
        # Sync latest models from Hugging Face on startup for known targets
        targets_to_sync = ["LapTimeSeconds", "Position"]
        
        for target in targets_to_sync:
            try:
                versions = HuggingFaceService.list_versions(target)
                if versions:
                    latest_version = versions[0]
                    state = ModelRegistry.get_registry_state()
                    target_info = state.get(target, {"versions": []})
                    
                    # Check if registered AND the model file physically exists
                    already_registered = any(v["version"] == latest_version for v in target_info.get("versions", []))
                    
                    expected_model_path = MODEL_DIR / target / latest_version / "model.pkl"
                    model_exists_physically = expected_model_path.exists()
                    
                    if not already_registered or not model_exists_physically:
                        logger.info(f"Syncing latest {target} model {latest_version} from Hugging Face...")
                        hf_data = HuggingFaceService.download_version(target, latest_version)
                        ModelRegistry.register_model(
                            target=target,
                            version=latest_version,
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
app.include_router(data.router, prefix="/api/data", tags=["Data"])
app.include_router(models.router, prefix="/models", tags=["Models Registry"])
app.include_router(metadata.router, tags=["Metadata"])
app.include_router(metrics.router, tags=["System"])
app.include_router(prediction.router, tags=["Prediction"])
app.include_router(simulation.router, tags=["Simulation Engines"])
app.include_router(ingest.router, prefix="/ingest", tags=["Data Ingestion"])
app.include_router(analyst.router, prefix="/analyst", tags=["AI Analyst"])

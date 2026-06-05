import time
import uuid
import pandas as pd
import numpy as np
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.logger import get_logger
from src.models import registry

logger = get_logger("api")

app = FastAPI(title="F1 AI Platform Prediction API", version="1.0.0")

# Preload Model
MODEL_TARGET = "LapTimeSeconds"
try:
    logger.info(f"Preloading model for target: {MODEL_TARGET}")
    artifacts = registry.load_model(target_name=MODEL_TARGET, version='latest')
    model = artifacts['model']
    features = artifacts['features']
    metadata = artifacts['metadata']
    # Extract validation RMSE to build confidence intervals
    model_rmse = metadata.get('metrics', [0, 0.0])[1] if 'metrics' in metadata else 0.5
    logger.info("Model preloaded successfully.")
except Exception as e:
    logger.error(f"Critical failure loading model during startup: {e}")
    model = None
    features = []
    metadata = {}
    model_rmse = 0.5

# Pydantic schema for robust validation
class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra='allow')
    Driver: str
    Team: str
    Compound: str
    Year: int
    RoundNumber: int
    SessionType: str
    TrackStatus: str
    AirTemp: float
    TrackTemp: float
    Humidity: float
    WindSpeed: float
    Rainfall: bool

# Monitoring Middleware
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(f"[{request_id}] Received {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time_ms = (time.time() - start_time) * 1000
        logger.info(f"[{request_id}] Completed {response.status_code} in {process_time_ms:.2f}ms")
        response.headers["X-Process-Time"] = str(process_time_ms)
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        process_time_ms = (time.time() - start_time) * 1000
        logger.error(f"[{request_id}] Failed with exception: {str(e)} in {process_time_ms:.2f}ms", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@app.get("/health")
async def health_check():
    """Model health and readiness probe."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")
    
    return {
        "status": "healthy",
        "model_type": metadata.get("model_type", "Unknown"),
        "version": metadata.get("version", "Unknown"),
        "training_date": metadata.get("training_date", "Unknown"),
        "rmse": round(model_rmse, 4)
    }

@app.post("/predict")
async def predict(payload: PredictionRequest):
    """Generates a prediction with a 95% confidence interval."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")
        
    try:
        # Convert Pydantic payload to dict, including any extra fields provided
        input_dict = payload.model_dump()
        df = pd.DataFrame([input_dict])
        
        # Ensure all required features exist
        for f in features:
            if f not in df.columns:
                df[f] = 0.0 # Default fallback
                
        # Subset and prepare for inference
        X = df[features]
        cat_cols = X.select_dtypes(include=['object']).columns
        for col in cat_cols:
            X[col] = X[col].astype(str).astype('category')
            
        # Run Prediction
        prediction = float(model.predict(X)[0])
        
        # Calculate 95% Confidence Interval (Approx ± 1.96 * RMSE)
        ci_lower = prediction - (1.96 * model_rmse)
        ci_upper = prediction + (1.96 * model_rmse)
        
        return {
            "prediction": round(prediction, 4),
            "confidence_interval_95": {
                "lower_bound": round(ci_lower, 4),
                "upper_bound": round(ci_upper, 4)
            },
            "unit": "seconds"
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=400, detail=f"Inference failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

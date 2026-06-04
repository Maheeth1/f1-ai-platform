from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict
import joblib
import pandas as pd
from huggingface_hub import hf_hub_download
import os

# ==================================================
# APP CONFIG
# ==================================================

app = FastAPI(
    title="F1 AI Platform API",
    description="Formula 1 Race Prediction API",
    version="1.0.0"
)

# Enable CORS for frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (update in production if needed)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# ==================================================
# MODEL LOADING
# ==================================================

model_path = hf_hub_download(
    repo_id="Maheeth1/f1-race-predictor",
    filename="f1_model.pkl"
)

model = None

try:
    model = joblib.load(model_path)
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Failed to load model: {e}")


# ==================================================
# REQUEST SCHEMA
# ==================================================

class PredictionRequest(BaseModel):
    Driver: int = Field(..., ge=0)
    LapNumber: int = Field(..., ge=1)
    TyreLife: int = Field(..., ge=0)


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/")
def root():
    return {
        "message": "F1 AI Platform Running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }


# ==================================================
# MODEL INFO
# ==================================================

@app.get("/model-info")
def model_info():

    if model is None:
        raise HTTPException(
            status_code=500,
            detail="Model not loaded"
        )

    return {
        "model_type": type(model).__name__,
        "features": [
            "Driver",
            "LapNumber",
            "TyreLife"
        ]
    }


# ==================================================
# PREDICTION ENDPOINT
# ==================================================

@app.post("/predict")
def predict(data: PredictionRequest):

    if model is None:
        raise HTTPException(
            status_code=500,
            detail="Model not loaded"
        )

    try:

        input_df = pd.DataFrame({
            "Driver": [data.Driver],
            "LapNumber": [data.LapNumber],
            "TyreLife": [data.TyreLife]
        })

        prediction = model.predict(input_df)

        return {
            "predicted_position": round(
                float(prediction[0]), 2
            )
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==================================================
# SAMPLE DATA ENDPOINT
# ==================================================

@app.get("/sample-request")
def sample_request():

    return {
        "Driver": 5,
        "LapNumber": 20,
        "TyreLife": 15
    }
from fastapi import FastAPI
import joblib
import pandas as pd
from pathlib import Path

app = FastAPI()

# Resolve paths relative to the script location
base_dir = Path(__file__).resolve().parent.parent
model_path = base_dir / 'ml' / 'f1_model.pkl'

model = joblib.load(model_path)

@app.get("/")
def home():
    return {
        "message":"F1 AI API Running"
    }

@app.get("/predict")
def predict():

    sample = pd.DataFrame({
        'Driver':[5],
        'LapNumber':[20],
        'TyreLife':[15]
    })

    result = model.predict(sample)

    return {
        "prediction": float(result[0])
    }
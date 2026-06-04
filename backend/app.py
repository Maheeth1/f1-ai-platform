from fastapi import FastAPI
import joblib
import pandas as pd

app = FastAPI()

model = joblib.load(
    '../ml/f1_model.pkl'
)

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
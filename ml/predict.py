import joblib
import pandas as pd
from pathlib import Path

# Resolve paths relative to the script location
base_dir = Path(__file__).resolve().parent.parent
model_path = base_dir / 'ml' / 'f1_model.pkl'

model = joblib.load(model_path)

sample = pd.DataFrame({
    'Driver':[5],
    'LapNumber':[20],
    'TyreLife':[15]
})

prediction = model.predict(sample)

print(prediction)
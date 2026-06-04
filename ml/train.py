import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
from pathlib import Path

# Resolve paths relative to the script location (project_root/ml)
base_dir = Path(__file__).resolve().parent.parent
input_path = base_dir / 'data' / 'processed' / 'ml_dataset.csv'
model_path = base_dir / 'ml' / 'f1_model.pkl'

df = pd.read_csv(input_path)

df['Driver'] = df['Driver'].astype('category').cat.codes

X = df[['Driver', 'LapNumber', 'TyreLife']]
y = df['Position']

model = RandomForestRegressor()

model.fit(X, y)

joblib.dump(
    model,
    model_path
)

print("Model trained")
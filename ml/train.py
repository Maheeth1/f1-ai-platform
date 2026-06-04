import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

df = pd.read_csv(
    '../data/processed/ml_dataset.csv'
)

df['Driver'] = df['Driver'].astype('category').cat.codes

X = df[['Driver', 'LapNumber', 'TyreLife']]
y = df['Position']

model = RandomForestRegressor()

model.fit(X, y)

joblib.dump(
    model,
    'f1_model.pkl'
)

print("Model trained")
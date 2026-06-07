import joblib

encoder = joblib.load('c:/Users/satish/f1-ai-platform/backend/models/LapTimeSeconds/v20260606_121209/encoder.pkl')
print(encoder)
for name, transformer, columns in encoder.transformers_:
    print(f"Name: {name}")
    print(f"Columns: {columns}")

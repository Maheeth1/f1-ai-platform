import joblib

encoder = joblib.load('c:/Users/satish/f1-ai-platform/backend/models/LapTimeSeconds/v20260606_121209/encoder.pkl')
try:
    names = encoder.get_feature_names_out()
    print("Features:", names[:5])
    print("Clean features:", [col.split('__')[-1] for col in names][:5])
except Exception as e:
    print("Error:", e)

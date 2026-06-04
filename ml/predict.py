import joblib
import pandas as pd

model = joblib.load('f1_model.pkl')

sample = pd.DataFrame({
    'Driver':[5],
    'LapNumber':[20],
    'TyreLife':[15]
})

prediction = model.predict(sample)

print(prediction)
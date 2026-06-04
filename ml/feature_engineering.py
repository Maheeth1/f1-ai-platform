import pandas as pd
from pathlib import Path

# Resolve paths relative to the script location (project_root/data)
base_dir = Path(__file__).resolve().parent.parent
input_path = base_dir / 'data' / 'raw' / 'monaco_2025.csv'
output_dir = base_dir / 'data' / 'processed'
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / 'ml_dataset.csv'

df = pd.read_csv(input_path)

features = df[
    [
        'Driver',
        'LapNumber',
        'TyreLife',
        'Position'
    ]
]

features.dropna(inplace=True)

features.to_csv(
    output_path,
    index=False
)

print("Features created")
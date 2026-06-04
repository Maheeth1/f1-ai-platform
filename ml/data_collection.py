import fastf1
import pandas as pd
from pathlib import Path

fastf1.Cache.enable_cache('cache')

session = fastf1.get_session(2025, 'Monaco Grand Prix', 'R')
session.load()

laps = session.laps

# Resolve path relative to the script location (project_root/data/raw)
output_dir = Path(__file__).resolve().parent.parent / 'data' / 'raw'
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / 'monaco_2025.csv'

laps.to_csv(
    output_path,
    index=False
)

print("Data saved successfully")
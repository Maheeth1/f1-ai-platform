# Formula 1 AI Analytics ML Pipeline

A state-of-the-art machine learning pipeline for Formula 1 race prediction, using FastF1 and advanced feature engineering.

## Architecture & Phases

- **Phase 1-3: Data Collection** (`src/data/`)
  Downloads historical race sessions, merges weather data, and extracts high-resolution telemetry.
- **Phase 4-5: Feature Engineering** (`src/features/`)
  Constructs rolling pace features, tire degradation indices, track flags, and creates a clean `master_f1_dataset.csv`.
- **Phase 6-8: Modeling** (`src/models/`)
  Trains XGBoost, LightGBM, CatBoost, and RandomForest models. Includes Optuna hyperparameter tuning and weighted ensembling.
- **Phase 9: Explainability** (`src/explainability/`)
  Generates SHAP summary plots to visualize feature importance.

## Quickstart Guide

### 1. Installation
Install the ML dependencies into your virtual environment:
```bash
pip install -r requirements.txt
```

### 2. Extract Data (Phase 1-3)
Run the data collection script. This will download the years defined in `src/utils/config.py` (2022-2025).
*Warning: Fetching telemetry for thousands of laps takes time and disk space.*
```bash
python src/data/collect_sessions.py
```

### 3. Build Master Dataset (Phase 4-5)
Once the raw CSVs are downloaded, merge and engineer them:
```bash
python src/features/build_master.py
```

### 4. Train Models (Phase 6-8)
To train the base models for Lap Time Prediction:
```bash
python src/models/train.py --target LapTimeSeconds
```

To tune hyperparameters with Optuna:
```bash
python src/models/hyperparameter_tuning.py --target LapTimeSeconds --trials 20
```

To run the unified Ensemble Model:
```bash
python src/models/ensemble.py
```

### 5. Generate Insights (Phase 9)
Generate SHAP explainability plots (saved to `ml/reports/`):
```bash
python src/explainability/shap_analysis.py
```

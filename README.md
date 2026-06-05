# F1 AI Prediction Platform 🏎️🤖

A production-grade, end-to-end Machine Learning pipeline that ingests historical Formula 1 telemetry, weather data, and race context to predict lap times and simulate entire Grand Prix events.

## Features
- **Automated Data Ingestion**: Pulls high-frequency telemetry and weather data directly from F1 APIs, complete with caching and rate-limiting protections.
- **Advanced Feature Engineering**: Calculates dynamic features like track evolution, fuel burn advantage, and tire degradation index.
- **Multi-Model Optimization**: Uses Optuna to aggressively tune and prune hyperparameters across CatBoost, LightGBM, and XGBoost natively.
- **Stacking Ensembles**: Leverages an automated `StackingRegressor` with a Ridge meta-learner for superior predictive power.
- **Monte Carlo Race Simulator**: Injects model-derived variance to simulate full 50-lap races, calculating Win and Podium probabilities.
- **Production API**: Fully containerized FastAPI serving layer with Pydantic validation and 95% Confidence Interval bounding.

---

## Getting Started: Step-by-Step Guide

### 1. Environment Setup
Make sure you have Python 3.10+ installed.

```bash
# Clone the repository (or navigate to the root folder)
cd f1-ai-platform

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r ml/requirements.txt
```

### 2. Data Collection
The first step is pulling the raw historical data. Note: The initial run can take 1-3 hours depending on connection speed. Because the system utilizes local caching, subsequent runs or crashes can be resumed instantly.

```bash
python ml/src/data/collect_sessions.py
```
*Data will be saved to `data/raw/`.*

### 3. Feature Engineering
Once the raw data is collected, you must clean, merge, and engineer the advanced racing features (e.g., Track Evolution, Tire Life).

```bash
python ml/src/features/build_master.py
```
*This outputs the final `master_f1_dataset.csv` into `data/processed/`.*

### 4. Hyperparameter Tuning (Optional)
If you want to find the optimal model architecture before training, run the Optuna tuner. This uses Hyperband pruning and runs across all available CPU cores.

```bash
python ml/src/models/hyperparameter_tuning.py --target LapTimeSeconds --trials 50 --jobs -1
```
*This generates a `best_params.json` and a `tuning_report.md`.*

### 5. Model Training & Registry
Train the production Stacking Ensemble model. This script automatically handles time-aware cross-validation, trains the base estimators (CatBoost, XGBoost, LightGBM), and saves the final artifact.

```bash
python ml/src/models/train.py
```
*The versioned model pipeline (model, encoders, metadata) will be serialized into the `ml/artifacts/` directory. SHAP explainability plots are also generated.*

### 6. Monte Carlo Race Simulation
Want to predict the outcome of a race? Run the race simulator, which loads the latest trained model from the registry and simulates a Grand Prix 1,000 times.

```bash
python ml/src/simulation/race_simulator.py
```

### 7. Production Deployment (Docker API)
Serve your newly trained model via a robust, containerized REST API. 

```bash
cd ml/
docker-compose up --build -d
```
The API will be available at `http://localhost:8000`. 
- **Check Health**: `curl http://localhost:8000/health`
- **View Docs**: Navigate to `http://localhost:8000/docs` in your browser to see the interactive Swagger UI and test predictions.

*(For full deployment details, see `deployment_guide.md`).*

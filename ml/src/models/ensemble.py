import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
import catboost as cb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.utils.logger import get_logger
from src.utils.config import PROCESSED_DATA_DIR, ROOT_DIR

logger = get_logger(__name__)

class WeightedEnsemble:
    def __init__(self, weights=None):
        self.models = {
            'xgb': xgb.XGBRegressor(n_estimators=100, random_state=42, n_jobs=-1),
            'lgb': lgb.LGBMRegressor(n_estimators=100, random_state=42, n_jobs=-1),
            'cb': cb.CatBoostRegressor(iterations=100, random_state=42, verbose=0)
        }
        # Default equal weighting
        self.weights = weights if weights else {'xgb': 0.33, 'lgb': 0.33, 'cb': 0.34}
        
    def fit(self, X, y):
        logger.info("Training ensemble models...")
        for name, model in self.models.items():
            logger.info(f"Training {name}...")
            model.fit(X, y)
            
    def predict(self, X):
        logger.info("Generating ensemble predictions...")
        preds = np.zeros(len(X))
        for name, model in self.models.items():
            preds += model.predict(X) * self.weights[name]
        return preds

def run_ensemble():
    data_path = PROCESSED_DATA_DIR / "master_f1_dataset.csv"
    if not data_path.exists():
        logger.error("Dataset not found!")
        return
        
    df = pd.read_csv(data_path)
    drop_cols = ['Time', 'LapTime', 'PitOutTime', 'PitInTime', 'LapStartTime', 'LapStartDate']
    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')
    
    cat_cols = df.select_dtypes(include=['object']).columns
    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    
    target = 'LapTimeSeconds'
    X = df.drop(columns=[target], errors='ignore')
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    ensemble = WeightedEnsemble()
    ensemble.fit(X_train, y_train)
    
    # Save models to disk for export
    import joblib
    import os
    model_dir = ROOT_DIR / "ml" / "saved_models"
    model_dir.mkdir(parents=True, exist_ok=True)
    
    for name, model in ensemble.models.items():
        joblib.dump(model, model_dir / f"{name}_f1_model.joblib")
    logger.info(f"Models saved locally to {model_dir}")
    
    preds = ensemble.predict(X_test)
    
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)
    
    logger.info("--- Ensemble Performance ---")
    logger.info(f"MAE:  {mae:.4f}")
    logger.info(f"RMSE: {rmse:.4f}")
    logger.info(f"R²:   {r2:.4f}")

if __name__ == "__main__":
    run_ensemble()

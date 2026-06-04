import optuna
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.utils.logger import get_logger
from src.utils.config import PROCESSED_DATA_DIR

logger = get_logger(__name__)

def objective(trial, X_train, X_test, y_train, y_test):
    """
    Optuna objective function for tuning XGBoost.
    """
    param = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 300),
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'random_state': 42,
        'n_jobs': -1
    }
    
    model = xgb.XGBRegressor(**param)
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    return rmse

def run_tuning(target='LapTimeSeconds', n_trials=20):
    logger.info(f"Starting Hyperparameter Tuning for target: {target}")
    
    data_path = PROCESSED_DATA_DIR / "master_f1_dataset.csv"
    if not data_path.exists():
        logger.error(f"Dataset not found at {data_path}")
        return
        
    df = pd.read_csv(data_path)
    # Basic prep
    drop_cols = ['Time', 'LapTime', 'PitOutTime', 'PitInTime', 'LapStartTime', 'LapStartDate']
    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')
    
    cat_cols = df.select_dtypes(include=['object']).columns
    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    
    X = df.drop(columns=[target], errors='ignore')
    y = df[target] if target in df.columns else None
    
    if y is None:
        logger.error(f"Target '{target}' not found!")
        return

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    study = optuna.create_study(direction='minimize')
    study.optimize(lambda trial: objective(trial, X_train, X_test, y_train, y_test), n_trials=n_trials)
    
    logger.info("Tuning complete!")
    logger.info(f"Best RMSE: {study.best_value:.4f}")
    logger.info(f"Best Parameters: {study.best_params}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', type=str, default='LapTimeSeconds')
    parser.add_argument('--trials', type=int, default=20)
    args = parser.parse_args()
    
    run_tuning(args.target, args.trials)

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import sys
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import lightgbm as lgb
import catboost as cb

# Add the src directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.logger import get_logger
from src.utils.config import PROCESSED_DATA_DIR

logger = get_logger(__name__)

def evaluate_model(y_true, y_pred, model_name="Model"):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    logger.info(f"--- {model_name} Performance ---")
    logger.info(f"MAE:  {mae:.4f}")
    logger.info(f"RMSE: {rmse:.4f}")
    logger.info(f"R²:   {r2:.4f}")
    
    return mae, rmse, r2

def train_lap_time_models(X_train, X_test, y_train, y_test):
    logger.info("Training Lap Time Prediction Models...")
    
    models = {
        'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        'XGBoost': xgb.XGBRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        'LightGBM': lgb.LGBMRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        'CatBoost': cb.CatBoostRegressor(iterations=100, random_state=42, verbose=0)
    }
    
    results = {}
    for name, model in models.items():
        logger.info(f"Training {name}...")
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        results[name] = evaluate_model(y_test, preds, name)
        
    return models, results

def validate_no_leakage(X, y):
    logger.info("Validating dataset for data leakage...")
    
    LEAKAGE_COLS = [
        'Time', 'LapTime', 'PitOutTime', 'PitInTime', 'Sector1Time', 'Sector2Time', 'Sector3Time',
        'LapStartTime', 'LapStartDate', 'Position', 'SpeedI1', 'SpeedI2', 'SpeedFL', 'SpeedST',
        'IsPersonalBest', 'Sector1SessionTime', 'Sector2SessionTime', 'Sector3SessionTime',
        'AvgSpeed', 'MaxSpeed', 'MinSpeed', 'AvgThrottle', 'MaxThrottle', 'BrakePercentage',
        'DRSPercentage', 'AvgRPM', 'MaxRPM', 'AvgGear', 'CorneringSpeed', 'TrackStatus', 'IsAccurate'
    ]
    
    leaking_cols_present = [col for col in LEAKAGE_COLS if col in X.columns]
    if y.name in X.columns:
        leaking_cols_present.append(y.name)
        
    if leaking_cols_present:
        raise ValueError(f"Data leakage detected! The following columns contain future information: {leaking_cols_present}")
        
    numeric_cols = X.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0 and len(X) > 1:
        # Check for abnormally high correlation
        correlations = X[numeric_cols].apply(lambda col: col.corr(y)).abs()
        leakers = correlations[correlations > 0.98].index.tolist()
        
        if leakers:
            raise ValueError(f"Data leakage detected! Features with >0.98 correlation with target: {leakers}")
    
    logger.info("Leakage validation passed.")

def main():
    parser = argparse.ArgumentParser(description="Train F1 Models")
    parser.add_argument('--target', type=str, default='LapTimeSeconds', 
                        choices=['LapTimeSeconds', 'GridPosition', 'Position'],
                        help="Target variable to predict")
    args = parser.parse_args()

    data_path = PROCESSED_DATA_DIR / "master_f1_dataset.csv"
    if not data_path.exists():
        logger.error(f"Master dataset not found at {data_path}")
        return

    df = pd.read_csv(data_path)
    
    # Drop all columns containing current-lap information (leakage)
    drop_cols = [
        'Time', 'LapTime', 'PitOutTime', 'PitInTime', 'Sector1Time', 'Sector2Time', 'Sector3Time',
        'LapStartTime', 'LapStartDate', 'Position', 'SpeedI1', 'SpeedI2', 'SpeedFL', 'SpeedST',
        'IsPersonalBest', 'Sector1SessionTime', 'Sector2SessionTime', 'Sector3SessionTime',
        'AvgSpeed', 'MaxSpeed', 'MinSpeed', 'AvgThrottle', 'MaxThrottle', 'BrakePercentage',
        'DRSPercentage', 'AvgRPM', 'MaxRPM', 'AvgGear', 'CorneringSpeed', 'TrackStatus', 'IsAccurate'
    ]
    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')
    
    # Encode categoricals
    cat_cols = df.select_dtypes(include=['object']).columns
    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)

    # Prepare features and target
    if args.target not in df.columns:
        logger.error(f"Target '{args.target}' not found in dataset!")
        return
        
    X = df.drop(columns=[args.target])
    y = df[args.target]
    
    # Run Leakage Validation
    validate_no_leakage(X, y)

    # Time-based split (e.g. use earlier years to predict later years, or just random split for now)
    # A robust split for F1 is essential. Random split for demonstration.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    logger.info(f"Training on {X_train.shape[0]} rows, testing on {X_test.shape[0]} rows.")
    
    if args.target == 'LapTimeSeconds':
        train_lap_time_models(X_train, X_test, y_train, y_test)
    else:
        logger.info(f"Training Grid/Position models... (similar implementation)")
        # For Position Prediction, typically just XGBoost and CatBoost as requested
        models = {
            'XGBoost': xgb.XGBRegressor(n_estimators=100, random_state=42, n_jobs=-1),
            'CatBoost': cb.CatBoostRegressor(iterations=100, random_state=42, verbose=0)
        }
        for name, model in models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            evaluate_model(y_test, preds, name)

if __name__ == "__main__":
    main()

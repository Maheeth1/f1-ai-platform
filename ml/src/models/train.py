import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import sys
from sklearn.model_selection import KFold, GroupKFold, TimeSeriesSplit
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

def train_lap_time_models(X_train, X_test, y_train, y_test, cat_features=None):
    logger.info("Training Lap Time Prediction Models...")
    
    if cat_features is None:
        cat_features = []
        
    models = {
        'CatBoost': cb.CatBoostRegressor(iterations=200, random_state=42, verbose=0, cat_features=cat_features),
        'LightGBM': lgb.LGBMRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        'XGBoost': xgb.XGBRegressor(n_estimators=100, random_state=42, n_jobs=-1, enable_categorical=True)
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

def compare_validation_strategies(X, y, groups):
    logger.info("Comparing Validation Strategies (Baseline: LightGBM)...")
    
    model = lgb.LGBMRegressor(n_estimators=100, random_state=42, n_jobs=-1, verbose=-1)
    results = {}
    
    # 1. Random Split (KFold)
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    random_metrics = {"MAE": [], "RMSE": [], "R2": []}
    for train_idx, test_idx in kf.split(X):
        X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
        X_te, y_te = X.iloc[test_idx], y.iloc[test_idx]
        model.fit(X_tr, y_tr)
        preds = model.predict(X_te)
        random_metrics["MAE"].append(mean_absolute_error(y_te, preds))
        random_metrics["RMSE"].append(np.sqrt(mean_squared_error(y_te, preds)))
        random_metrics["R2"].append(r2_score(y_te, preds))
    results['Random Split'] = {k: np.mean(v) for k, v in random_metrics.items()}
    
    # 2. GroupKFold (by EventName)
    if groups is not None and not groups.empty:
        gkf = GroupKFold(n_splits=5)
        group_metrics = {"MAE": [], "RMSE": [], "R2": []}
        for train_idx, test_idx in gkf.split(X, y, groups):
            X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
            X_te, y_te = X.iloc[test_idx], y.iloc[test_idx]
            model.fit(X_tr, y_tr)
            preds = model.predict(X_te)
            group_metrics["MAE"].append(mean_absolute_error(y_te, preds))
            group_metrics["RMSE"].append(np.sqrt(mean_squared_error(y_te, preds)))
            group_metrics["R2"].append(r2_score(y_te, preds))
        results['GroupKFold'] = {k: np.mean(v) for k, v in group_metrics.items()}
    else:
        results['GroupKFold'] = {"MAE": np.nan, "RMSE": np.nan, "R2": np.nan}
        
    # 3. TimeSeriesSplit (Time-aware)
    tscv = TimeSeriesSplit(n_splits=5)
    time_metrics = {"MAE": [], "RMSE": [], "R2": []}
    for train_idx, test_idx in tscv.split(X):
        X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
        X_te, y_te = X.iloc[test_idx], y.iloc[test_idx]
        model.fit(X_tr, y_tr)
        preds = model.predict(X_te)
        time_metrics["MAE"].append(mean_absolute_error(y_te, preds))
        time_metrics["RMSE"].append(np.sqrt(mean_squared_error(y_te, preds)))
        time_metrics["R2"].append(r2_score(y_te, preds))
    results['TimeSplit'] = {k: np.mean(v) for k, v in time_metrics.items()}
    
    return results

def generate_validation_report(results, report_path):
    report_content = "# Validation Strategy Comparison Report\n\n"
    report_content += "This report compares three different cross-validation strategies using a baseline LightGBM model. "
    report_content += "Notice how Random Split often shows overly optimistic performance due to temporal leakage.\n\n"
    
    report_content += "| Strategy | RMSE | MAE | R² |\n"
    report_content += "| :--- | :--- | :--- | :--- |\n"
    
    for strategy, metrics in results.items():
        rmse = metrics.get('RMSE', np.nan)
        mae = metrics.get('MAE', np.nan)
        r2 = metrics.get('R2', np.nan)
        report_content += f"| **{strategy}** | {rmse:.4f} | {mae:.4f} | {r2:.4f} |\n"
        
    report_content += "\n## Conclusion\n"
    report_content += "Based on motorsport realities, **TimeSplit** (TimeSeriesSplit) was automatically selected "
    report_content += "as the most realistic validation strategy for the final model training because it strictly prevents "
    report_content += "the model from seeing future data during training.\n"
    
    with open(report_path, "w", encoding='utf-8') as f:
        f.write(report_content)
    logger.info(f"Validation report saved to {report_path}")

def generate_model_comparison_report(results, report_path):
    report_content = "# Model Performance Comparison\n\n"
    report_content += "This report compares the performance of our primary models after upgrading to native categorical handling.\n\n"
    report_content += "| Model | RMSE | MAE | R² |\n"
    report_content += "| :--- | :--- | :--- | :--- |\n"
    
    for name, metrics in results.items():
        mae, rmse, r2 = metrics
        report_content += f"| **{name}** | {rmse:.4f} | {mae:.4f} | {r2:.4f} |\n"
        
    report_content += "\n## Conclusion\n"
    report_content += "**CatBoost** is now configured as the primary model due to its robust native handling of categorical features."
    
    with open(report_path, "w", encoding='utf-8') as f:
        f.write(report_content)
    logger.info(f"Model comparison report saved to {report_path}")

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
    
    # 1. Sort chronologically BEFORE anything else
    sort_cols = [c for c in ['Year', 'RoundNumber'] if c in df.columns]
    if sort_cols:
        logger.info(f"Sorting dataset chronologically by: {sort_cols}")
        df = df.sort_values(by=sort_cols).reset_index(drop=True)
        
    # Extract groups before they get encoded or dropped
    groups = df['EventName'].copy() if 'EventName' in df.columns else None
    
    # Drop all columns containing current-lap information (leakage)
    drop_cols = [
        'Time', 'LapTime', 'PitOutTime', 'PitInTime', 'Sector1Time', 'Sector2Time', 'Sector3Time',
        'LapStartTime', 'LapStartDate', 'Position', 'SpeedI1', 'SpeedI2', 'SpeedFL', 'SpeedST',
        'IsPersonalBest', 'Sector1SessionTime', 'Sector2SessionTime', 'Sector3SessionTime',
        'AvgSpeed', 'MaxSpeed', 'MinSpeed', 'AvgThrottle', 'MaxThrottle', 'BrakePercentage',
        'DRSPercentage', 'AvgRPM', 'MaxRPM', 'AvgGear', 'CorneringSpeed', 'TrackStatus', 'IsAccurate'
    ]
    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')
    
    # Automatically identify categorical columns
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Use native categorical handling instead of one-hot encoding
    for col in cat_cols:
        df[col] = df[col].astype(str).fillna("missing").astype('category')

    # Prepare features and target
    if args.target not in df.columns:
        logger.error(f"Target '{args.target}' not found in dataset!")
        return
        
    X = df.drop(columns=[args.target])
    y = df[args.target]
    
    # Run Leakage Validation
    validate_no_leakage(X, y)

    # Compare validation strategies
    val_results = compare_validation_strategies(X, y, groups)
    report_path = Path(__file__).resolve().parent.parent.parent / "validation_report.md"
    generate_validation_report(val_results, report_path)
    
    # Automatically select TimeSplit for final training
    logger.info("Automatically selecting TimeSplit as the most realistic strategy.")
    tscv = TimeSeriesSplit(n_splits=5)
    splits = list(tscv.split(X))
    train_idx, test_idx = splits[-1] # Train on older seasons, test on newest
    
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    logger.info(f"Training on {X_train.shape[0]} rows, testing on {X_test.shape[0]} rows.")
    
    if args.target in cat_cols:
        cat_cols.remove(args.target)

    if args.target == 'LapTimeSeconds':
        models, results = train_lap_time_models(X_train, X_test, y_train, y_test, cat_features=cat_cols)
        comp_path = Path(__file__).resolve().parent.parent.parent / "model_comparison.md"
        generate_model_comparison_report(results, comp_path)
    else:
        logger.info(f"Training Grid/Position models... (similar implementation)")
        models = {
            'CatBoost': cb.CatBoostRegressor(iterations=100, random_state=42, verbose=0, cat_features=cat_cols),
            'LightGBM': lgb.LGBMRegressor(n_estimators=100, random_state=42, n_jobs=-1),
            'XGBoost': xgb.XGBRegressor(n_estimators=100, random_state=42, n_jobs=-1, enable_categorical=True)
        }
        results = {}
        for name, model in models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            results[name] = evaluate_model(y_test, preds, name)
        comp_path = Path(__file__).resolve().parent.parent.parent / "model_comparison.md"
        generate_model_comparison_report(results, comp_path)

if __name__ == "__main__":
    main()

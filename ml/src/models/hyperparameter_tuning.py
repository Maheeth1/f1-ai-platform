import optuna
import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
import catboost as cb
import json
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error
from optuna.integration import LightGBMPruningCallback, XGBoostPruningCallback
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.utils.logger import get_logger
from src.utils.config import PROCESSED_DATA_DIR

logger = get_logger(__name__)

def objective(trial, X, y, cat_cols):
    """
    Optuna objective function for tuning CatBoost, LightGBM, and XGBoost natively.
    """
    model_type = trial.suggest_categorical('model_type', ['CatBoost', 'LightGBM', 'XGBoost'])
    
    # Time-Aware Validation
    tscv = TimeSeriesSplit(n_splits=3)
    rmses = []
    
    for step, (train_idx, test_idx) in enumerate(tscv.split(X)):
        X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
        X_te, y_te = X.iloc[test_idx], y.iloc[test_idx]
        
        if model_type == 'CatBoost':
            param = {
                'iterations': trial.suggest_int('cb_iterations', 100, 500),
                'depth': trial.suggest_int('cb_depth', 4, 10),
                'learning_rate': trial.suggest_float('cb_lr', 0.01, 0.3, log=True),
                'l2_leaf_reg': trial.suggest_float('cb_l2', 1, 10, log=True),
                'random_state': 42,
                'verbose': 0,
                'cat_features': cat_cols
            }
            model = cb.CatBoostRegressor(**param)
            model.fit(X_tr, y_tr, eval_set=[(X_te, y_te)], early_stopping_rounds=20, verbose=False)
            
        elif model_type == 'LightGBM':
            param = {
                'n_estimators': trial.suggest_int('lgb_n_estimators', 100, 500),
                'max_depth': trial.suggest_int('lgb_max_depth', 3, 10),
                'learning_rate': trial.suggest_float('lgb_lr', 0.01, 0.3, log=True),
                'num_leaves': trial.suggest_int('lgb_num_leaves', 20, 100),
                'random_state': 42,
                'n_jobs': -1,
                'verbose': -1
            }
            model = lgb.LGBMRegressor(**param)
            callbacks = [LightGBMPruningCallback(trial, "valid_0")]
            model.fit(X_tr, y_tr, eval_set=[(X_te, y_te)], eval_metric="rmse", callbacks=callbacks)
            
        elif model_type == 'XGBoost':
            param = {
                'n_estimators': trial.suggest_int('xgb_n_estimators', 100, 500),
                'max_depth': trial.suggest_int('xgb_max_depth', 3, 10),
                'learning_rate': trial.suggest_float('xgb_lr', 0.01, 0.3, log=True),
                'subsample': trial.suggest_float('xgb_subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('xgb_colsample', 0.6, 1.0),
                'enable_categorical': True,
                'random_state': 42,
                'n_jobs': -1
            }
            model = xgb.XGBRegressor(**param)
            pruning_callback = XGBoostPruningCallback(trial, "validation_0-rmse")
            model.fit(X_tr, y_tr, eval_set=[(X_te, y_te)], verbose=False, callbacks=[pruning_callback])
            
        preds = model.predict(X_te)
        rmse = np.sqrt(mean_squared_error(y_te, preds))
        rmses.append(rmse)
        
        # Report intermediate value for pruning
        trial.report(rmse, step)
        if trial.should_prune():
            raise optuna.TrialPruned()
            
    return np.mean(rmses)

def generate_tuning_report(study, report_path):
    report_content = f"# Hyperparameter Tuning Report\n\n"
    report_content += "This report summarizes the results of the automated Optuna optimization.\n\n"
    report_content += "## Overview\n"
    report_content += f"- **Best Model Type**: {study.best_params.get('model_type', 'Unknown')}\n"
    report_content += f"- **Best Cross-Validated RMSE**: {study.best_value:.4f}\n"
    report_content += f"- **Total Trials Completed**: {len(study.trials)}\n"
    
    pruned_trials = [t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED]
    report_content += f"- **Pruned Trials (Saved Compute)**: {len(pruned_trials)}\n\n"
    
    report_content += "## Best Parameters\n```json\n"
    report_content += json.dumps(study.best_params, indent=4)
    report_content += "\n```\n"
    
    with open(report_path, "w", encoding='utf-8') as f:
        f.write(report_content)
    logger.info(f"Tuning report saved to {report_path}")

def run_tuning(target='LapTimeSeconds', n_trials=50, n_jobs=-1):
    logger.info(f"Starting Hyperparameter Tuning for target: {target}")
    
    data_path = PROCESSED_DATA_DIR / "master_f1_dataset.csv"
    if not data_path.exists():
        logger.error(f"Dataset not found at {data_path}")
        return
        
    df = pd.read_csv(data_path)
    
    # 1. Sort chronologically BEFORE anything else
    sort_cols = [c for c in ['Year', 'RoundNumber'] if c in df.columns]
    if sort_cols:
        df = df.sort_values(by=sort_cols).reset_index(drop=True)
        
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
    
    # Use native categorical handling
    for col in cat_cols:
        df[col] = df[col].astype(str).fillna("missing").astype('category')
        
    if target in cat_cols:
        cat_cols.remove(target)
        
    X = df.drop(columns=[target], errors='ignore')
    y = df[target] if target in df.columns else None
    
    if y is None:
        logger.error(f"Target '{target}' not found!")
        return

    # Use Hyperband Pruner for aggressive early stopping of unpromising trials
    pruner = optuna.pruners.HyperbandPruner()
    study = optuna.create_study(direction='minimize', pruner=pruner)
    
    logger.info(f"Running Optuna Optimization with {n_trials} trials across {n_jobs} cores...")
    study.optimize(lambda trial: objective(trial, X, y, cat_cols), n_trials=n_trials, n_jobs=n_jobs)
    
    logger.info("Tuning complete!")
    logger.info(f"Best RMSE: {study.best_value:.4f}")
    logger.info(f"Best Parameters: {study.best_params}")
    
    # Save best parameters
    best_params_path = Path(__file__).resolve().parent.parent.parent / "best_params.json"
    with open(best_params_path, "w", encoding='utf-8') as f:
        json.dump(study.best_params, f, indent=4)
        
    report_path = Path(__file__).resolve().parent.parent.parent / "tuning_report.md"
    generate_tuning_report(study, report_path)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', type=str, default='LapTimeSeconds')
    parser.add_argument('--trials', type=int, default=50)
    parser.add_argument('--jobs', type=int, default=-1, help="Number of parallel jobs (-1 for all cores)")
    args = parser.parse_args()
    
    run_tuning(args.target, args.trials, args.jobs)

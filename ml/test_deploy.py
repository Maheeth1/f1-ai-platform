from src.models import registry
from src.pipeline.deploy import evaluate_and_promote_candidate
from src.utils.config import PROCESSED_DATA_DIR
from src.models.train import evaluate_model
import pandas as pd
from pathlib import Path

def test():
    # Load dataset to get X_test, y_test just like in train.py
    data_path = PROCESSED_DATA_DIR / "master_f1_dataset.csv"
    df = pd.read_csv(data_path)
    
    # Sort
    sort_cols = [c for c in ['Year', 'RoundNumber'] if c in df.columns]
    df = df.sort_values(by=sort_cols).reset_index(drop=True)
    
    # Drops
    drop_cols = [
        'Time', 'LapTime', 'PitOutTime', 'PitInTime', 'Sector1Time', 'Sector2Time', 'Sector3Time',
        'LapStartTime', 'LapStartDate', 'Position', 'SpeedI1', 'SpeedI2', 'SpeedFL', 'SpeedST',
        'IsPersonalBest', 'Sector1SessionTime', 'Sector2SessionTime', 'Sector3SessionTime',
        'AvgSpeed', 'MaxSpeed', 'MinSpeed', 'AvgThrottle', 'MaxThrottle', 'BrakePercentage',
        'DRSPercentage', 'AvgRPM', 'MaxRPM', 'AvgGear', 'CorneringSpeed', 'TrackStatus', 'IsAccurate'
    ]
    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')
    
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    for col in cat_cols:
        df[col] = df[col].astype(str).fillna("missing").astype('category')
        
    X = df.drop(columns=['LapTimeSeconds'])
    y = df['LapTimeSeconds']
    
    # TimeSplit
    from sklearn.model_selection import TimeSeriesSplit
    tscv = TimeSeriesSplit(n_splits=5)
    splits = list(tscv.split(X))
    train_idx, test_idx = splits[-1]
    
    X_test = X.iloc[test_idx]
    y_test = y.iloc[test_idx]
    
    # Load latest model as candidate
    payload = registry.load_model("LapTimeSeconds", version="latest")
    candidate_model = payload["model"]
    
    # Evaluate it to get metrics
    preds = candidate_model.predict(X_test)
    candidate_metrics = evaluate_model(y_test, preds, "Candidate Model")
    
    # Run deployment
    evaluate_and_promote_candidate(
        candidate_model=candidate_model,
        X_test=X_test,
        y_test=y_test,
        candidate_metrics=candidate_metrics,
        feature_list=payload["features"],
        target_name="LapTimeSeconds",
        model_type="StackingEnsemble"
    )

if __name__ == "__main__":
    test()

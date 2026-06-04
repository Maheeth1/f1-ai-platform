# pyrefly: ignore [missing-import]
import shap
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.utils.logger import get_logger
from src.utils.config import PROCESSED_DATA_DIR, ROOT_DIR

logger = get_logger(__name__)

def generate_shap_plots(model, X_sample, output_dir):
    logger.info("Calculating SHAP values...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)
    
    # 1. Summary Plot
    plt.figure()
    shap.summary_plot(shap_values, X_sample, show=False)
    plt.savefig(output_dir / "shap_summary.png", bbox_inches='tight')
    plt.close()
    
    # 2. Feature Importance Plot (Bar)
    plt.figure()
    shap.summary_plot(shap_values, X_sample, plot_type="bar", show=False)
    plt.savefig(output_dir / "shap_feature_importance.png", bbox_inches='tight')
    plt.close()
    
    logger.info(f"SHAP plots saved to {output_dir}")

def run_explainability():
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

    # Train a quick model for explainability
    logger.info("Training XGBoost model for SHAP analysis...")
    model = xgb.XGBRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)
    
    # Generate SHAP on a sample to save memory
    X_sample = X.sample(n=min(5000, len(X)), random_state=42)
    
    output_dir = ROOT_DIR / "ml" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generate_shap_plots(model, X_sample, output_dir)

if __name__ == "__main__":
    run_explainability()

import pandas as pd
from pathlib import Path
import sys
import argparse

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.utils.logger import get_logger
from src.models import registry, explainability
from src.utils.config import PROCESSED_DATA_DIR

logger = get_logger(__name__)

def explain_production(target_name: str = "LapTimeSeconds"):
    logger.info(f"Loading production model for target: {target_name} to generate SHAP explanations...")
    try:
        artifacts = registry.load_model(target_name=target_name, version="latest")
    except Exception as e:
        logger.error(f"Failed to load production model: {e}")
        return
        
    model = artifacts["model"]
    features = artifacts["features"]
    encoder = artifacts.get("encoder")
    
    # Check if we can use TreeExplainer directly
    explainer_model = model
    # If it's a StackingRegressor, try to extract CatBoost for faster tree-based explanation
    if hasattr(model, "estimators_"):
        for name, est in zip(model.estimators, model.estimators_):
            if name[0] == "CatBoost":
                explainer_model = est
                logger.info("Extracted CatBoost base estimator from StackingRegressor for SHAP TreeExplainer.")
                break
                
    # Load sample data
    data_path = PROCESSED_DATA_DIR / "master_f1_dataset.csv"
    df = pd.read_csv(data_path)
    
    missing_features = [f for f in features if f not in df.columns]
    for mf in missing_features:
        df[mf] = 0.0
        
    X = df[features].copy()
    
    # We must apply the same encoding that the model expects!
    if encoder:
        logger.info("Applying ColumnTransformer preprocessing to explanation sample...")
        X_arr = encoder.transform(X)
        X = pd.DataFrame(X_arr, columns=features)
        
    X_sample = X.sample(n=min(1000, len(X)), random_state=42)
    
    project_root = Path(__file__).resolve().parent.parent
    logger.info("Generating global SHAP explanations...")
    explainability.generate_global_explanations(explainer_model, X_sample, project_root)
    
    logger.info("Generating local SHAP explanations for sample index 0...")
    explainability.generate_local_explanations(explainer_model, X_sample, project_root, row_idx=0)
    
    logger.info("Building explanation report...")
    explainability.create_explainability_report(project_root)
    logger.info(f"SHAP explanation completed. Report saved at {project_root / 'explainability_report.md'}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="LapTimeSeconds")
    args = parser.parse_args()
    explain_production(args.target)

import json
from pathlib import Path
from src.utils.logger import get_logger
from src.models import registry
from src.models.train import evaluate_model
from src.models.wrappers import AutoCatBoostRegressor
import os
import joblib

logger = get_logger(__name__)

def evaluate_and_promote_candidate(candidate_model, X_test, y_test, candidate_metrics, feature_list, target_name, model_type="StackingEnsemble"):
    """
    Evaluates the newly trained candidate model against the current active production model.
    If the candidate is better (lower RMSE), it promotes it to production.
    """
    logger.info("=== Starting Automated Deployment Pipeline ===")
    
    # Normalize candidate_metrics if it's a tuple or list
    if isinstance(candidate_metrics, (tuple, list)):
        candidate_metrics = {
            "MAE": candidate_metrics[0],
            "RMSE": candidate_metrics[1],
            "R2": candidate_metrics[2]
        }
    
    # 1. Check if production model exists
    prod_metrics = None
    try:
        logger.info(f"Checking for existing production model for target '{target_name}'...")
        prod_payload = registry.load_model(target_name, version="latest")
        prod_model = prod_payload["model"]
        
        logger.info("Evaluating production model on the current test set...")
        prod_preds = prod_model.predict(X_test)
        prod_mae, prod_rmse, prod_r2 = evaluate_model(y_test, prod_preds, "Production Model")
        
        prod_metrics = {
            "MAE": prod_mae,
            "RMSE": prod_rmse,
            "R2": prod_r2
        }
    except FileNotFoundError:
        logger.warning(f"No existing production model found for '{target_name}'. Candidate will be promoted automatically.")
    except Exception as e:
        logger.error(f"Error loading production model: {e}. Candidate will be evaluated standalone.")
        
    candidate_rmse = candidate_metrics.get("RMSE")
    
    # 2. Decision Logic
    promote = False
    improvement = 0.0
    
    if prod_metrics is None:
        promote = True
        logger.info("Decision: PROMOTED (No production baseline exists)")
    else:
        prod_rmse = prod_metrics.get("RMSE")
        if candidate_rmse < prod_rmse:
            promote = True
            improvement = ((prod_rmse - candidate_rmse) / prod_rmse) * 100
            logger.info(f"Decision: PROMOTED (Candidate improved RMSE by {improvement:.2f}%)")
        else:
            degradation = ((candidate_rmse - prod_rmse) / prod_rmse) * 100
            logger.warning(f"Decision: REJECTED (Candidate degraded RMSE by {degradation:.2f}%)")
            
    # 3. Execution
    version = "N/A"
    if promote:
        logger.info("Registering candidate model and pushing to Hugging Face...")
        version = registry.save_model(
            model=candidate_model,
            target_name=target_name,
            metrics=candidate_metrics,
            feature_list=feature_list,
            model_type=model_type
        )
        logger.info(f"Model {version} successfully deployed to production.")
        
    # 4. Generate Reports
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    reports_dir = project_root / "ml" / "artifacts" / target_name / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    generate_metrics_json(candidate_metrics, prod_metrics, promote, improvement, reports_dir)
    generate_markdown_report(candidate_metrics, prod_metrics, promote, improvement, version, reports_dir)
    
def generate_metrics_json(candidate_metrics, prod_metrics, promoted, improvement, out_dir):
    data = {
        "promoted": promoted,
        "improvement_percentage": round(improvement, 2),
        "candidate": candidate_metrics,
        "production": prod_metrics
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(data, f, indent=4)
        
def generate_markdown_report(candidate_metrics, prod_metrics, promoted, improvement, version, out_dir):
    status = "✅ PROMOTED" if promoted else "❌ REJECTED"
    
    content = f"# Model Evaluation Report\n\n"
    content += f"**Status:** {status}\n"
    if promoted:
        content += f"**New Version:** `{version}`\n"
        if prod_metrics:
            content += f"**Improvement:** {improvement:.2f}% reduction in RMSE\n\n"
        else:
            content += "**Improvement:** Initial Baseline\n\n"
            
    content += "## Head-to-Head Comparison\n\n"
    content += "| Metric | Candidate Model | Production Model |\n"
    content += "| :--- | :--- | :--- |\n"
    
    cand_rmse = candidate_metrics.get('RMSE', 0)
    cand_mae = candidate_metrics.get('MAE', 0)
    cand_r2 = candidate_metrics.get('R2', 0)
    
    if prod_metrics:
        prod_rmse = f"{prod_metrics.get('RMSE', 0):.4f}"
        prod_mae = f"{prod_metrics.get('MAE', 0):.4f}"
        prod_r2 = f"{prod_metrics.get('R2', 0):.4f}"
    else:
        prod_rmse = "N/A"
        prod_mae = "N/A"
        prod_r2 = "N/A"
        
    content += f"| **RMSE** | {cand_rmse:.4f} | {prod_rmse} |\n"
    content += f"| **MAE** | {cand_mae:.4f} | {prod_mae} |\n"
    content += f"| **R²** | {cand_r2:.4f} | {prod_r2} |\n\n"
    
    if not promoted:
        content += "## Action Required\n"
        content += "The candidate model failed to outperform the production baseline on the holdout test set. "
        content += "Consider tuning hyperparameters, adding new features, or checking for data distribution shifts."
        
    with open(out_dir / "evaluation_report.md", "w") as f:
        f.write(content)

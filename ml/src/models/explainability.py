import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from src.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import shap
except ImportError:
    shap = None
    logger.warning("SHAP library not found. Explainability features will be disabled.")

def generate_global_explanations(model, X_sample, output_dir):
    """
    Generates and saves the SHAP summary plot (beeswarm).
    """
    if shap is None:
        logger.error("Cannot generate SHAP global explanations: shap is not installed.")
        return
        
    logger.info("Generating SHAP global explanations...")
    
    # We use TreeExplainer since we are passing the CatBoost primary model
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)
    
    # Generate Summary Plot
    plt.figure(figsize=(12, 8))
    shap.summary_plot(shap_values, X_sample, show=False)
    
    output_path = Path(output_dir) / "shap_summary.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    logger.info(f"Saved global explanations to {output_path}")

def generate_local_explanations(model, X_sample, output_dir, row_idx=0):
    """
    Generates and saves a SHAP waterfall plot for a specific prediction.
    """
    if shap is None:
        logger.error("Cannot generate SHAP local explanations: shap is not installed.")
        return
        
    logger.info(f"Generating SHAP local explanation for index {row_idx}...")
    
    # Needs Explanation object for waterfall plot
    explainer = shap.Explainer(model)
    
    # Get explanation for single row
    shap_values = explainer(X_sample.iloc[[row_idx]])
    
    plt.figure(figsize=(10, 6))
    shap.plots.waterfall(shap_values[0], show=False)
    
    output_path = Path(output_dir) / "shap_waterfall.png"
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    logger.info(f"Saved local explanation to {output_path}")

def create_explainability_report(output_dir):
    """
    Generates an explainability_report.md file embedding the generated plots.
    """
    report_content = """# Explainability Report

This report provides Explainable AI (XAI) insights into our primary predictive model using SHAP (SHapley Additive exPlanations).

## Global Feature Importance

The summary plot below shows the most important features driving the model's predictions across the validation set. 
- **Features at the top** have the highest impact on the output.
- **Color** represents the feature value (red is high, blue is low).
- **Horizontal location** shows whether that value pushed the prediction higher or lower.

![SHAP Summary Plot](shap_summary.png)

## Local Prediction Explanation

The waterfall plot below breaks down exactly how the model arrived at its prediction for a single specific validation case.
- The **bottom value** is the expected (base) prediction across the dataset.
- Each **bar** shows how a specific feature value pushed the prediction up (red) or down (blue).
- The **top value** is the final predicted output.

![SHAP Waterfall Plot](shap_waterfall.png)

> [!NOTE]
> These explanations are generated using `shap.TreeExplainer` on the primary CatBoost model to ensure accurate attribution of both numerical and native categorical features.
"""

    report_path = Path(output_dir) / "explainability_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    logger.info(f"Created explainability report at {report_path}")

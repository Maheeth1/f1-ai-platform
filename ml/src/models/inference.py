import pandas as pd
import numpy as np
import argparse
from pathlib import Path
import sys

# Add the src directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.logger import get_logger
from src.models import registry

logger = get_logger(__name__)

def make_predictions(input_data, target_name='LapTimeSeconds', version='latest'):
    """
    Demonstrates loading a production model artifact from the registry
    and running inference on new input data.
    """
    logger.info(f"Initializing inference for target: {target_name} (version: {version})")
    
    try:
        # 1. Load artifacts automatically
        artifacts = registry.load_model(target_name=target_name, version=version)
    except FileNotFoundError as e:
        logger.error(f"Failed to load model artifacts: {e}")
        return None
        
    model = artifacts['model']
    features = artifacts['features']
    metadata = artifacts['metadata']
    
    logger.info(f"Successfully loaded model: {metadata['model_type']} (v{metadata['version']}) trained on {metadata['training_date']}")
    
    # 2. Prepare input data
    if isinstance(input_data, pd.DataFrame):
        df = input_data.copy()
    else:
        df = pd.DataFrame([input_data])
        
    # Ensure all required features are present, fill missing with 0 or NA
    missing_features = [f for f in features if f not in df.columns]
    if missing_features:
        logger.warning(f"Missing features in input data, filling with NaNs: {missing_features}")
        for mf in missing_features:
            df[mf] = np.nan
            
    # Subset and reorder to match training exactly
    X_inference = df[features]
    
    # 3. Apply ColumnTransformer (loaded as encoder)
    encoder = artifacts.get('encoder')
    if encoder:
        logger.info("Applying ColumnTransformer preprocessing...")
        try:
            X_transformed = encoder.transform(X_inference)
            X_inference = pd.DataFrame(X_transformed, columns=features)
        except Exception as e:
            logger.error(f"Error during preprocessing transform: {e}")
            raise e
        
    # 4. Predict
    logger.info("Running prediction...")
    predictions = model.predict(X_inference)
    
    return predictions

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="F1 Model Inference Demo")
    parser.add_argument('--target', type=str, default='LapTimeSeconds', help="Target variable model to load")
    parser.add_argument('--version', type=str, default='latest', help="Model version to load")
    args = parser.parse_args()
    
    # Dummy data for demonstration purposes
    dummy_data = {
        'Year': 2024,
        'RoundNumber': 1,
        'TrackStatus': '1',
        'AirTemp': 25.5,
        'TrackTemp': 32.0,
        'Humidity': 45.0,
        'Pressure': 1012.0,
        'Driver': 'VER',
        'Team': 'Red Bull Racing'
    }
    
    preds = make_predictions(dummy_data, target_name=args.target, version=args.version)
    if preds is not None:
        logger.info(f"Prediction Result: {preds}")

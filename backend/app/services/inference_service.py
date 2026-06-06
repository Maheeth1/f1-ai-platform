import time
import pandas as pd
from typing import List, Dict, Any
from app.schemas.prediction import PredictionRequest, PredictionResponse, BatchPredictionRequest, BatchPredictionResponse
from app.services.model_registry import ModelRegistry
from app.services.confidence import ConfidenceEstimator
from app.core.logger import logger
from app.core.metrics import PREDICTIONS_COUNTER, PREDICTION_LATENCY

class InferenceService:
    
    def _preprocess(self, df: pd.DataFrame, encoder, scaler, features: List[str]) -> pd.DataFrame:
        # Extract categorical columns from ColumnTransformer if available
        cat_cols = set()
        if encoder and hasattr(encoder, 'transformers_'):
            for name, trans, cols in encoder.transformers_:
                if name == 'cat':
                    cat_cols.update(cols)
                    
        # 1. Fill missing features with default 0.0 or "missing"
        for col in features:
            if col not in df.columns:
                if col in cat_cols:
                    df[col] = "missing"
                else:
                    df[col] = 0.0

        # Subselect required features
        df = df[features].copy()
        
        # 2. Type casting for categorical columns naturally
        for col in df.columns:
            if col in cat_cols or df[col].dtype == 'object' or df[col].dtype.name == 'category':
                df[col] = df[col].astype(str).astype('category')
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        # 3. Apply Encoder if available (Now a ColumnTransformer)
        if encoder:
            transformed_arr = encoder.transform(df)
            # ColumnTransformer returns an array, so we must recreate the DataFrame
            # Restore feature names from the encoder if possible (ColumnTransformer prefixes them)
            try:
                out_cols = [col.split('__')[-1] for col in encoder.get_feature_names_out()]
                df = pd.DataFrame(transformed_arr, columns=out_cols)
            except Exception:
                df = pd.DataFrame(transformed_arr)
            
        # 4. Apply Scaler if available (Legacy support if separated)
        if scaler:
            df_scaled = scaler.transform(df)
            df = pd.DataFrame(df_scaled, columns=df.columns)
            
        return df

    def predict(self, target: str, data: PredictionRequest) -> PredictionResponse:
        start_time = time.time()
        
        model_payload = ModelRegistry.get_active_model(target)
        if model_payload is None:
            raise ValueError(f"Active model for target '{target}' is not loaded.")
            
        model = model_payload["model"]
        encoder = model_payload.get("encoder")
        scaler = model_payload.get("scaler")
        features = model_payload.get("features", [])
        version = model_payload.get("version", "unknown")
        
        try:
            with PREDICTION_LATENCY.labels(target=target).time():
                input_df = pd.DataFrame([data.model_dump()])
                processed_df = self._preprocess(input_df, encoder, scaler, features)
                
                prediction = float(model.predict(processed_df)[0])
                
                # Retrieve metadata for confidence calculation
                registry_state = ModelRegistry.get_registry_state()
                target_info = registry_state.get(target, {})
                metadata = {}
                for v in target_info.get("versions", []):
                    if v["version"] == version:
                        metadata = v
                        break
                        
                lower, upper, conf, report = ConfidenceEstimator.estimate_confidence(
                    model, processed_df, prediction, metadata
                )
            PREDICTIONS_COUNTER.labels(target=target, version=version, status="success").inc()
        except Exception as e:
            PREDICTIONS_COUNTER.labels(target=target, version=version, status="error").inc()
            raise e
        
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        return PredictionResponse(
            prediction=round(prediction, 4),
            lower_bound=lower,
            upper_bound=upper,
            confidence=conf,
            confidence_report=report,
            model_version=version,
            latency_ms=latency_ms
        )

    def predict_batch(self, target: str, data: BatchPredictionRequest) -> BatchPredictionResponse:
        start_time = time.time()
        
        model_payload = ModelRegistry.get_active_model(target)
        if model_payload is None:
            raise ValueError(f"Active model for target '{target}' is not loaded.")
            
        model = model_payload["model"]
        encoder = model_payload.get("encoder")
        scaler = model_payload.get("scaler")
        features = model_payload.get("features", [])
        version = model_payload.get("version", "unknown")
        
        try:
            with PREDICTION_LATENCY.labels(target=target).time():
                input_df = pd.DataFrame([req.model_dump() for req in data.requests])
                processed_df = self._preprocess(input_df, encoder, scaler, features)
                
                predictions = model.predict(processed_df)
                
                # Retrieve metadata for confidence calculation
                registry_state = ModelRegistry.get_registry_state()
                target_info = registry_state.get(target, {})
                metadata = {}
                for v in target_info.get("versions", []):
                    if v["version"] == version:
                        metadata = v
                        break
                        
                responses = []
                for i, pred in enumerate(predictions):
                    pred_val = float(pred)
                    single_processed_df = processed_df.iloc[[i]]
                    
                    lower, upper, conf, report = ConfidenceEstimator.estimate_confidence(
                        model, single_processed_df, pred_val, metadata
                    )
                    
                    # Latency for batch item is averaged
                    latency_ms = round(((time.time() - start_time) * 1000) / len(predictions), 2)
                    
                    responses.append(PredictionResponse(
                        prediction=round(pred_val, 4),
                        lower_bound=lower,
                        upper_bound=upper,
                        confidence=conf,
                        confidence_report=report,
                        model_version=version,
                        latency_ms=latency_ms
                    ))
            PREDICTIONS_COUNTER.labels(target=target, version=version, status="success").inc(len(predictions))
        except Exception as e:
            PREDICTIONS_COUNTER.labels(target=target, version=version, status="error").inc(len(data.requests))
            raise e
            
        return BatchPredictionResponse(responses=responses)

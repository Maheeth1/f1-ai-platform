import time
import pandas as pd
from typing import List, Dict, Any
from app.schemas.prediction import PredictionRequest, PredictionResponse, BatchPredictionRequest, BatchPredictionResponse
from app.services.model_registry import ModelRegistry
from app.core.logger import logger

class InferenceService:
    
    def _preprocess(self, df: pd.DataFrame, encoder, scaler, features: List[str]) -> pd.DataFrame:
        # 1. Fill missing features with default 0.0 or "missing"
        for col in features:
            if col not in df.columns:
                df[col] = 0.0

        # Subselect required features
        df = df[features].copy()
        
        # 2. Type casting for categorical columns naturally
        # If encoder is none, we still ensure basic object types are categories for models like CatBoost/LightGBM
        for col in df.columns:
            if df[col].dtype == 'object' or df[col].dtype.name == 'category':
                df[col] = df[col].astype(str).astype('category')
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        # 3. Apply Encoder if available
        if encoder:
            df = encoder.transform(df)
            
        # 4. Apply Scaler if available
        if scaler:
            df_scaled = scaler.transform(df)
            df = pd.DataFrame(df_scaled, columns=df.columns)
            
        return df

    def _calculate_confidence(self, prediction: float, target: str) -> float:
        # Fetch metrics from registry to calculate confidence
        registry_state = ModelRegistry.get_registry_state()
        target_info = registry_state.get(target, {})
        active_version = target_info.get("active_version")
        rmse = 0.5 # Default fallback
        if active_version:
            for v in target_info.get("versions", []):
                if v["version"] == active_version:
                    rmse = v.get("metrics", {}).get("RMSE", 0.5)
                    break
        
        # Pseudo-confidence formula based on variance relative to prediction magnitude
        # max(0, 100 - (rmse / abs(prediction) * 100))
        if prediction == 0:
            return 0.0
            
        confidence = max(0.0, 100.0 - (rmse / abs(prediction)) * 100.0)
        return round(min(100.0, confidence), 2)

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
        
        input_df = pd.DataFrame([data.model_dump()])
        processed_df = self._preprocess(input_df, encoder, scaler, features)
        
        prediction = float(model.predict(processed_df)[0])
        confidence = self._calculate_confidence(prediction, target)
        
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        return PredictionResponse(
            prediction=round(prediction, 4),
            confidence=confidence,
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
        
        input_df = pd.DataFrame([req.model_dump() for req in data.requests])
        processed_df = self._preprocess(input_df, encoder, scaler, features)
        
        predictions = model.predict(processed_df)
        
        responses = []
        for pred in predictions:
            pred_val = float(pred)
            confidence = self._calculate_confidence(pred_val, target)
            # Latency for batch item is averaged
            latency_ms = round(((time.time() - start_time) * 1000) / len(predictions), 2)
            
            responses.append(PredictionResponse(
                prediction=round(pred_val, 4),
                confidence=confidence,
                model_version=version,
                latency_ms=latency_ms
            ))
            
        return BatchPredictionResponse(responses=responses)
